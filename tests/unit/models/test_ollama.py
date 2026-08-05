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
from sentinelrag.models.ollama import OllamaAdapter


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
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
        model_identifier="test-model",
    )


def test_ollama_generate_success_and_payload_mapping(
    settings: SentinelSettings,
) -> None:
    async def _run() -> None:
        captured_request = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_request
            captured_request = request
            content = {
                "model": "test-model",
                "message": {"role": "assistant", "content": "Hello world!"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 10,
                "eval_count": 5,
                "extra_field": "ignored",
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")],
            temperature=0.8,
            max_tokens=500,
            seed=42,
        )
        resp = await adapter.generate(req)

        assert captured_request is not None
        assert captured_request.method == "POST"
        assert str(captured_request.url) == "http://127.0.0.1/api/chat"

        payload = json.loads(captured_request.content)
        assert payload["model"] == "test-model"
        assert payload["stream"] is False
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]
        assert payload["options"]["temperature"] == 0.8
        assert payload["options"]["num_predict"] == 500
        assert payload["options"]["seed"] == 42

        assert resp.provider_kind == ProviderKind.OLLAMA
        assert resp.model_identifier == "test-model"
        assert resp.assistant_content == "Hello world!"
        assert resp.finish_reason == "stop"
        assert resp.prompt_token_count == 10
        assert resp.output_token_count == 5

    asyncio.run(_run())


def test_ollama_generate_invalid_json(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=MockAsyncByteStream(b"{invalid"))

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid JSON"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_missing_model(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"message": {"role": "assistant", "content": "H"}, "done": True}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Missing or invalid 'model'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_wrong_assistant_role(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "message": {"role": "user", "content": "H"},
                "done": True,
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(
            ProviderProtocolError, match="Message role is not 'assistant'"
        ):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_whitespace_content(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "message": {"role": "assistant", "content": "   "},
                "done": True,
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(
            ProviderProtocolError, match="Failed to construct NormalizedResponse"
        ):
            # Pydantic validates assistant_content regex
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_invalid_token_counts(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "message": {"role": "assistant", "content": "H"},
                "done": True,
                "prompt_eval_count": True,  # bool
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid 'prompt_eval_count'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_done_missing_or_false(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {"model": "m", "message": {"role": "assistant", "content": "H"}}
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Response is not done"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_invalid_done_reason(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "message": {"role": "assistant", "content": "H"},
                "done": True,
                "done_reason": 123,
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid 'done_reason'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_oversized_character_response(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            content = {
                "model": "m",
                "message": {"role": "assistant", "content": "H" * 40000},
                "done": True,
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        settings.max_response_characters = 100
        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ResponseTooLargeError, match="exceeds maximum characters"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_error_bodies_not_exposed(settings: SentinelSettings) -> None:
    async def _run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, stream=MockAsyncByteStream(b"SECRET_DB_ERROR"))

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderHttpError) as exc:
            await adapter.generate(req)
        assert "SECRET_DB_ERROR" not in str(exc.value)

    asyncio.run(_run())


def test_ollama_check_availability_deduplicates_and_skips_invalid(
    settings: SentinelSettings,
) -> None:
    async def _run() -> None:
        captured_request = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_request
            captured_request = request
            content = {
                "models": [
                    {"name": "model1"},
                    {"name": "   "},  # whitespace only skipped
                    {"name": "model2"},
                    {"name": "model1"},  # deduplicated
                    {"invalid": "model"},  # missing name skipped
                    "string not dict",  # skipped
                ]
            }
            return httpx.Response(
                200, stream=MockAsyncByteStream(json.dumps(content).encode("utf-8"))
            )

        adapter = OllamaAdapter(settings, transport=httpx.MockTransport(handler))
        avail = await adapter.check_availability()

        assert captured_request is not None
        assert captured_request.method == "GET"
        assert str(captured_request.url) == "http://127.0.0.1/api/tags"

        assert avail.models == ["model1", "model2"]

    asyncio.run(_run())


def test_ollama_closed_idempotent_and_rejects(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
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


def test_ollama_generate_max_tokens_exceeded(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings, transport=httpx.MockTransport(lambda r: httpx.Response(200))
        )
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="H")], max_tokens=2048
        )
        settings.max_requested_output_tokens = 1024
        with pytest.raises(ProviderProtocolError, match="exceed the maximum allowed"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_data_not_dict(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[])),
        )
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Expected JSON object"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_message_not_dict(settings: SentinelSettings) -> None:
    async def _run() -> None:
        content = {"model": "m", "message": "not dict", "done": True}
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=content)),
        )
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Missing or invalid 'message'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_content_not_string(settings: SentinelSettings) -> None:
    async def _run() -> None:
        content = {
            "model": "m",
            "message": {"role": "assistant", "content": 123},
            "done": True,
        }
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=content)),
        )
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="invalid 'message.content'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_generate_eval_count_invalid(settings: SentinelSettings) -> None:
    async def _run() -> None:
        content = {
            "model": "m",
            "message": {"role": "assistant", "content": "H"},
            "done": True,
            "eval_count": -1,
        }
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=content)),
        )
        req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="H")])
        with pytest.raises(ProviderProtocolError, match="Invalid 'eval_count'"):
            await adapter.generate(req)

    asyncio.run(_run())


def test_ollama_check_availability_invalid_json(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, content=b"{invalid")
            ),
        )
        with pytest.raises(ProviderProtocolError, match="Invalid JSON"):
            await adapter.check_availability()

    asyncio.run(_run())


def test_ollama_check_availability_not_dict(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[])),
        )
        with pytest.raises(ProviderProtocolError, match="Expected JSON object"):
            await adapter.check_availability()

    asyncio.run(_run())


def test_ollama_check_availability_models_not_list(settings: SentinelSettings) -> None:
    async def _run() -> None:
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, json={"models": "not list"})
            ),
        )
        with pytest.raises(ProviderProtocolError, match="invalid 'models' list"):
            await adapter.check_availability()

    asyncio.run(_run())


def test_ollama_check_availability_too_many_models(settings: SentinelSettings) -> None:
    async def _run() -> None:
        # ProviderAvailability enforces max 100 models,
        # generating 101 will raise ValueError -> ProviderProtocolError
        content = {"models": [{"name": f"model{i}"} for i in range(101)]}
        adapter = OllamaAdapter(
            settings,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=content)),
        )
        with pytest.raises(
            ProviderProtocolError, match="Failed to construct ProviderAvailability"
        ):
            await adapter.check_availability()

    asyncio.run(_run())
