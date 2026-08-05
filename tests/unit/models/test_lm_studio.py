import asyncio
import json
from typing import Any

import httpx
import pytest

from sentinelrag.config.settings import ProviderKind, SentinelSettings
from sentinelrag.models.contracts import (
    ChatMessage,
    ChatRole,
    GenerationRequest,
    ProviderProtocolError,
)
from sentinelrag.models.lm_studio import LMStudioAdapter


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, response_factory: Any) -> None:
        self.response_factory = response_factory

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return self.response_factory(request)  # type: ignore


@pytest.fixture
def settings() -> SentinelSettings:
    return SentinelSettings(
        provider=ProviderKind.LM_STUDIO,
        endpoint="http://127.0.0.1/v1",  # type: ignore[arg-type]
        model_identifier="test-model",
    )


def test_lm_studio_generate_success(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "test-model-resolved",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Hello world!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                },
            }
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = LMStudioAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        resp = await adapter.generate(req)

        assert resp.provider_kind == ProviderKind.LM_STUDIO
        assert resp.model_identifier == "test-model-resolved"
        assert resp.assistant_content == "Hello world!"
        assert resp.finish_reason == "stop"
        assert resp.prompt_token_count == 10
        assert resp.output_token_count == 5

    asyncio.run(_run())


def test_lm_studio_generate_missing_choices(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {"model": "test-model"}
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = LMStudioAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderProtocolError, match="Missing or empty 'choices'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_empty_choices(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {"model": "test-model", "choices": []}
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = LMStudioAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderProtocolError, match="Missing or empty 'choices'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_check_availability_success(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {
                "data": [
                    {"id": "model1"},
                    {"id": "model2"},
                ]
            }
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = LMStudioAdapter(settings, transport=MockTransport(response_factory))
        avail = await adapter.check_availability()
        assert avail.models == ["model1", "model2"]

    asyncio.run(_run())


def test_lm_studio_check_availability_invalid(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content: dict[str, Any] = {"models": []}
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = LMStudioAdapter(settings, transport=MockTransport(response_factory))
        with pytest.raises(
            ProviderProtocolError, match="Missing or invalid 'data' list"
        ):
            await adapter.check_availability()

    asyncio.run(_run())
