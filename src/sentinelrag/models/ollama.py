import json
from typing import Any

import httpx

from sentinelrag.config.settings import ProviderKind, SentinelSettings
from sentinelrag.models.contracts import (
    GenerationRequest,
    NormalizedResponse,
    ProviderAvailability,
    ProviderClosedError,
    ProviderProtocolError,
    ResponseTooLargeError,
)
from sentinelrag.models.http import create_http_client, execute_request_with_retries
from sentinelrag.models.provider import ModelProvider


class OllamaAdapter(ModelProvider):
    def __init__(
        self,
        settings: SentinelSettings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._client = create_http_client(settings, transport)
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise ProviderClosedError(ProviderKind.OLLAMA)

    async def generate(self, request: GenerationRequest) -> NormalizedResponse:
        self._ensure_open()

        if request.max_tokens > self._settings.max_requested_output_tokens:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA,
                "Requested tokens exceed the maximum allowed output tokens.",
            )

        messages = [
            {"role": m.role.value, "content": m.content} for m in request.messages
        ]

        payload: dict[str, Any] = {
            "model": self._settings.model_identifier,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        if request.seed is not None:
            payload["options"]["seed"] = request.seed

        request_kwargs = {
            "method": "POST",
            "url": "/chat",
            "json": payload,
        }

        response = await execute_request_with_retries(
            client=self._client,
            request_kwargs=request_kwargs,
            provider=ProviderKind.OLLAMA,
            retry_limit=self._settings.retry_limit,
            max_response_bytes=self._settings.max_response_bytes,
        )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Invalid JSON in response."
            ) from e

        if not isinstance(data, dict):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Expected JSON object in response."
            )

        model = data.get("model")
        message = data.get("message")

        if not model or not isinstance(model, str):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Missing or invalid 'model' in response."
            )

        if not isinstance(message, dict):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Missing or invalid 'message' in response."
            )

        role = message.get("role")
        if role != "assistant":
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Message role is not 'assistant'."
            )

        content = message.get("content")
        if not isinstance(content, str) or not content:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA,
                "Missing, empty, or invalid 'message.content' in response.",
            )

        done = data.get("done")
        if done is not True:
            raise ProviderProtocolError(ProviderKind.OLLAMA, "Response is not done.")

        done_reason = data.get("done_reason")
        if done_reason is not None and not isinstance(done_reason, str):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Invalid 'done_reason' in response."
            )

        prompt_eval_count = data.get("prompt_eval_count")
        if prompt_eval_count is not None and (
            not isinstance(prompt_eval_count, int)
            or isinstance(prompt_eval_count, bool)
            or prompt_eval_count < 0
        ):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Invalid 'prompt_eval_count' in response."
            )

        eval_count = data.get("eval_count")
        if eval_count is not None and (
            not isinstance(eval_count, int)
            or isinstance(eval_count, bool)
            or eval_count < 0
        ):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Invalid 'eval_count' in response."
            )

        if len(content) > self._settings.max_response_characters:
            raise ResponseTooLargeError(
                ProviderKind.OLLAMA,
                "Generated content exceeds maximum characters limit.",
            )

        try:
            return NormalizedResponse(
                provider_kind=ProviderKind.OLLAMA,
                model_identifier=model,
                assistant_content=content,
                finish_reason=done_reason,
                prompt_token_count=prompt_eval_count,
                output_token_count=eval_count,
            )
        except ValueError as e:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Failed to construct NormalizedResponse."
            ) from e

    async def check_availability(self) -> ProviderAvailability:
        self._ensure_open()

        request_kwargs = {
            "method": "GET",
            "url": "/tags",
        }

        response = await execute_request_with_retries(
            client=self._client,
            request_kwargs=request_kwargs,
            provider=ProviderKind.OLLAMA,
            retry_limit=self._settings.retry_limit,
            max_response_bytes=self._settings.max_response_bytes,
        )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Invalid JSON in response."
            ) from e

        if not isinstance(data, dict):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Expected JSON object in response."
            )

        models_list = data.get("models")
        if not isinstance(models_list, list):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Missing or invalid 'models' list in response."
            )

        available_models = []
        for m in models_list:
            if isinstance(m, dict):
                name = m.get("name")
                if isinstance(name, str) and name.strip():
                    available_models.append(name.strip())

        try:
            return ProviderAvailability(
                provider_kind=ProviderKind.OLLAMA,
                available=True,
                models=available_models,
            )
        except ValueError as e:
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Failed to construct ProviderAvailability."
            ) from e

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            await self._client.aclose()
