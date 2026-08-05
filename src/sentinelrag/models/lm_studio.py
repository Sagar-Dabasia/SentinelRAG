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


class LMStudioAdapter(ModelProvider):
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
            raise ProviderClosedError(ProviderKind.LM_STUDIO)

    async def generate(self, request: GenerationRequest) -> NormalizedResponse:
        self._ensure_open()

        messages = [
            {"role": m.role.value, "content": m.content} for m in request.messages
        ]

        payload: dict[str, Any] = {
            "model": self._settings.model_identifier,
            "messages": messages,
            "stream": False,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.seed is not None:
            payload["seed"] = request.seed

        request_kwargs = {
            "method": "POST",
            "url": "/chat/completions",
            "json": payload,
        }

        response = await execute_request_with_retries(
            client=self._client,
            request_kwargs=request_kwargs,
            provider=ProviderKind.LM_STUDIO,
            retry_limit=self._settings.retry_limit,
            max_response_bytes=self._settings.max_response_bytes,
        )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Invalid JSON in response."
            ) from e

        if not isinstance(data, dict):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Expected JSON object in response."
            )

        choices = data.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Missing or empty 'choices' in response."
            )

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "First choice is not an object."
            )

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Missing or invalid 'message' in first choice."
            )

        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO,
                "Missing or invalid 'message.content' in response.",
            )

        if len(content) > self._settings.max_response_characters:
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO,
                f"Generated content exceeds maximum characters ({len(content)} > {self._settings.max_response_characters}).",  # noqa: E501
            )

        usage = data.get("usage", {})
        if not isinstance(usage, dict):
            usage = {}

        model_ident = str(data.get("model", self._settings.model_identifier))
        return NormalizedResponse(
            provider_kind=ProviderKind.LM_STUDIO,
            model_identifier=model_ident,
            assistant_content=content,
            finish_reason=first_choice.get("finish_reason"),
            prompt_token_count=usage.get("prompt_tokens"),
            output_token_count=usage.get("completion_tokens"),
        )

    async def check_availability(self) -> ProviderAvailability:
        self._ensure_open()

        request_kwargs = {
            "method": "GET",
            "url": "/models",
        }

        response = await execute_request_with_retries(
            client=self._client,
            request_kwargs=request_kwargs,
            provider=ProviderKind.LM_STUDIO,
            retry_limit=self._settings.retry_limit,
            max_response_bytes=self._settings.max_response_bytes,
        )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Invalid JSON in response."
            ) from e

        if not isinstance(data, dict):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Expected JSON object in response."
            )

        data_list = data.get("data")
        if not isinstance(data_list, list):
            raise ProviderProtocolError(
                ProviderKind.LM_STUDIO, "Missing or invalid 'data' list in response."
            )

        available_models = []
        for m in data_list:
            if isinstance(m, dict) and isinstance(m.get("id"), str):
                available_models.append(m["id"])

        return ProviderAvailability(models=available_models)

    async def aclose(self) -> None:
        self._closed = True
        await self._client.aclose()
