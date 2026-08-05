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

        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderProtocolError(
                ProviderKind.OLLAMA, "Missing or invalid 'message.content' in response."
            )

        # Enforce max response characters
        if len(content) > self._settings.max_response_characters:
            # We truncate or error. The prompt says: "Enforce: Maximum HTTP response bytes, Maximum normalized assistant-content characters"  # noqa: E501
            # I will raise an error.
            raise ProviderProtocolError(
                ProviderKind.OLLAMA,
                f"Generated content exceeds maximum characters ({len(content)} > {self._settings.max_response_characters}).",  # noqa: E501
            )

        return NormalizedResponse(
            provider_kind=ProviderKind.OLLAMA,
            model_identifier=model,
            assistant_content=content,
            finish_reason=data.get("done_reason"),
            prompt_token_count=data.get("prompt_eval_count"),
            output_token_count=data.get("eval_count"),
        )

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
            if isinstance(m, dict) and isinstance(m.get("name"), str):
                available_models.append(m["name"])

        return ProviderAvailability(models=available_models)

    async def aclose(self) -> None:
        self._closed = True
        await self._client.aclose()
