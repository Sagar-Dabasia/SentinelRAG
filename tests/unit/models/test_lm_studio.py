import asyncio
import json

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
    ResponseTooLargeError,
)
from sentinelrag.models.lm_studio import LMStudioAdapter


class MockAsyncByteStream(httpx.AsyncByteStream):
    def __init__(self, content: bytes) -> None:
        self._content = content
        self.closed = False

    from collections.abc import AsyncIterator

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield self._content

    async def aclose(self) -> None:
        self.closed = True


@pytest.fixture
def settings() -> SentinelSettings:
    return SentinelSettings(
        provider=ProviderKind.LM_STUDIO,
        endpoint="http://127.0.0.1/v1",  # type: ignore[arg-type]
        model_identifier="test-model",
    )


def test_lm_studio_generate_success_and_payload_mapping(
    settings: SentinelSettings,
) -> None:
    async def _run() -> None:
        captured_request = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_request
            captured_request = request
            content = {
                "model": "test-model",
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
                "extra_field": "ignored",
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")],
            temperature=0.8,
            max_tokens=500,
            seed=42,
        )
        resp = await adapter.generate(req)

        assert captured_request is not None
        assert captured_request.method == "POST"
        assert str(captured_request.url) == "http://127.0.0.1/v1/chat/completions"

        payload = json.loads(captured_request.content)
        assert payload["model"] == "test-model"
        assert payload["stream"] is False
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]
        assert payload["temperature"] == 0.8
        assert payload["max_tokens"] == 500
        assert payload["seed"] == 42

        assert resp.provider_kind == ProviderKind.LM_STUDIO
        assert resp.model_identifier == "test-model"
        assert resp.assistant_content == "Hello world!"
        assert resp.finish_reason == "stop"
        assert resp.prompt_token_count == 10
        assert resp.output_token_count == 5

    asyncio.run(_run())


def test_lm_studio_generate_invalid_json(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=MockAsyncByteStream(b"{invalid"))

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid JSON"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_missing_model(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"choices": [{"message": {"role": "assistant", "content": "H"}}]}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Missing or invalid 'model'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_wrong_assistant_role(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "choices": [{"message": {"role": "user", "content": "H"}}],
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(
            ProviderProtocolError, match="Message role is not 'assistant'"
        ):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_whitespace_content(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "choices": [{"message": {"role": "assistant", "content": "   "}}],
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(
            ProviderProtocolError, match="Failed to construct NormalizedResponse"
        ):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_invalid_token_counts(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "choices": [{"message": {"role": "assistant", "content": "H"}}],
                "usage": {"prompt_tokens": True},  # bool
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid 'prompt_tokens'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_missing_choices(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"model": "m"}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Missing or empty 'choices'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_empty_choices(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"model": "m", "choices": []}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Missing or empty 'choices'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_non_object_first_choice(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"model": "m", "choices": ["not_dict"]}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(
            ProviderProtocolError, match="First choice is not an object"
        ):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_generate_invalid_usage_object(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "choices": [{"message": {"role": "assistant", "content": "H"}}],
                "usage": "not dict",
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid 'usage'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_oversized_character_response(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "choices": [{"message": {"role": "assistant", "content": "H" * 40000}}],
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        settings.max_response_characters = 100
        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ResponseTooLargeError, match="exceeds maximum characters"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_lm_studio_error_bodies_not_exposed(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, stream=MockAsyncByteStream(b"SECRET_DB_ERROR"))

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderHttpError) as exc:
            await adapter.generate(req)
        assert "SECRET_DB_ERROR" not in str(exc.value)

    asyncio.run(_run())


def test_lm_studio_check_availability_deduplicates_and_skips_invalid(
    settings: SentinelSettings,
) -> None:
    async def _run() -> None:
        captured_request = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_request
            captured_request = request
            content = {
                "data": [
                    {"id": "model1"},
                    {"id": "   "},  # whitespace only skipped
                    {"id": "model2"},
                    {"id": "model1"},  # deduplicated
                    {"invalid": "model"},  # missing id skipped
                    "string not dict",  # skipped
                ]
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = LMStudioAdapter(settings, transport=httpx.MockTransport(handler))
        avail = await adapter.check_availability()

        assert captured_request is not None
        assert captured_request.method == "GET"
        assert str(captured_request.url) == "http://127.0.0.1/v1/models"

        assert avail.models == ["model1", "model2"]

    asyncio.run(_run())


def test_lm_studio_closed_idempotent_and_rejects(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = LMStudioAdapter(
            settings, transport=httpx.MockTransport(lambda r: httpx.Response(200))
        )
        await adapter.aclose()
        await adapter.aclose()  # idempotent

        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderClosedError):
            await adapter.generate(req)

        with pytest.raises(ProviderClosedError):
            await adapter.check_availability()

    asyncio.run(_run())
