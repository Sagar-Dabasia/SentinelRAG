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
    ProviderClosedError,
    ProviderHttpError,
    ProviderProtocolError,
)
from sentinelrag.models.ollama import OllamaAdapter


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, response_factory: Any) -> None:
        self.response_factory = response_factory

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return self.response_factory(request)  # type: ignore


@pytest.fixture
def settings() -> SentinelSettings:
    return SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
        model_identifier="test-model",
    )


def test_ollama_generate_success(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "test-model",
                "message": {"role": "assistant", "content": "Hello world!"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 10,
                "eval_count": 5,
            }
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        resp = await adapter.generate(req)

        assert resp.provider_kind == ProviderKind.OLLAMA
        assert resp.model_identifier == "test-model"
        assert resp.assistant_content == "Hello world!"
        assert resp.finish_reason == "stop"
        assert resp.prompt_token_count == 10
        assert resp.output_token_count == 5

    asyncio.run(_run())


def test_ollama_generate_http_error(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, content=b"Bad request", request=request)

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderHttpError, match="HTTP 400"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_invalid_json(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"{invalid", request=request)

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderProtocolError, match="Invalid JSON"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_missing_fields(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {"model": "test"}
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderProtocolError, match="Missing or invalid 'message'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_check_availability_success(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {
                "models": [
                    {"name": "model1"},
                    {"name": "model2"},
                ]
            }
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        avail = await adapter.check_availability()
        assert avail.models == ["model1", "model2"]

    asyncio.run(_run())


def test_ollama_check_availability_invalid_format(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def response_factory(request: httpx.Request) -> httpx.Response:
            content = {"models": "not a list"}
            return httpx.Response(
                200, content=json.dumps(content).encode("utf-8"), request=request
            )

        adapter = OllamaAdapter(settings, transport=MockTransport(response_factory))
        with pytest.raises(
            ProviderProtocolError, match="Missing or invalid 'models' list"
        ):
            await adapter.check_availability()

    asyncio.run(_run())


def test_ollama_closed(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings, transport=MockTransport(lambda r: httpx.Response(200))
        )
        await adapter.aclose()

        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderClosedError):
            await adapter.generate(req)

        with pytest.raises(ProviderClosedError):
            await adapter.check_availability()

    asyncio.run(_run())
