import pytest
from pydantic import ValidationError

from sentinelrag.config.settings import ProviderKind
from sentinelrag.models.contracts import (
    ChatMessage,
    ChatRole,
    GenerationRequest,
    NormalizedResponse,
    ProviderAvailability,
)


def test_chat_message_valid() -> None:
    msg = ChatMessage(role=ChatRole.USER, content="Hello")
    assert msg.role == ChatRole.USER
    assert msg.content == "Hello"


def test_chat_message_empty_content() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role=ChatRole.USER, content="")
    with pytest.raises(ValidationError):
        ChatMessage(role=ChatRole.USER, content="   ")


def test_chat_message_too_long() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role=ChatRole.USER, content="a" * 131073)


def test_chat_message_immutability() -> None:
    msg = ChatMessage(role=ChatRole.USER, content="Hello")
    with pytest.raises(ValidationError):
        msg.content = "New"


def test_generation_request_valid() -> None:
    req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="Hello")])
    assert len(req.messages) == 1
    assert req.temperature == 0.7
    assert req.max_tokens == 1024


def test_generation_request_empty_messages() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(messages=[])


def test_generation_request_too_many_messages() -> None:
    messages = [ChatMessage(role=ChatRole.USER, content="A") for _ in range(101)]
    with pytest.raises(ValidationError):
        GenerationRequest(messages=messages)


def test_generation_request_temperature_bounds() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")],
            temperature=-0.1,
        )
    with pytest.raises(ValidationError):
        GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")],
            temperature=2.1,
        )


def test_generation_request_max_tokens_bounds() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")],
            max_tokens=0,
        )


def test_generation_request_total_content_limit() -> None:
    # 4 messages of 131072 each is 524288 (exactly limit)
    # 5 messages will exceed.
    messages = [ChatMessage(role=ChatRole.USER, content="a" * 131072) for _ in range(5)]
    with pytest.raises(ValueError, match="Total message content exceeds maximum"):
        GenerationRequest(messages=messages)


def test_generation_request_immutability() -> None:
    req = GenerationRequest(messages=[ChatMessage(role=ChatRole.USER, content="Hello")])
    with pytest.raises(ValidationError):
        req.temperature = 1.0


def test_provider_availability_deduplicates_and_preserves_order() -> None:
    pa = ProviderAvailability(
        provider_kind=ProviderKind.OLLAMA,
        available=True,
        models=["c", "a", "c", "b", "a"],
    )
    assert pa.models == ["c", "a", "b"]


def test_provider_availability_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProviderAvailability(
            provider_kind=ProviderKind.OLLAMA,
            available=True,
            models=["a"],
            extra_field="rejected",  # type: ignore[call-arg]
        )


def test_normalized_response_rejects_whitespace_only() -> None:
    with pytest.raises(ValidationError):
        NormalizedResponse(
            provider_kind=ProviderKind.OLLAMA,
            model_identifier="test",
            assistant_content="   \n\t  ",
        )
    # Valid non-whitespace
    nr = NormalizedResponse(
        provider_kind=ProviderKind.OLLAMA,
        model_identifier="test",
        assistant_content=" \n valid \t ",
    )
    assert nr.assistant_content == " \n valid \t "


def test_normalized_response_token_types() -> None:
    # Boolean rejected
    with pytest.raises(ValidationError):
        NormalizedResponse(
            provider_kind=ProviderKind.OLLAMA,
            model_identifier="test",
            assistant_content="valid",
            prompt_token_count=True,
        )
    with pytest.raises(ValidationError):
        NormalizedResponse(
            provider_kind=ProviderKind.OLLAMA,
            model_identifier="test",
            assistant_content="valid",
            prompt_token_count=10.5,  # type: ignore[arg-type]
        )
    with pytest.raises(ValidationError):
        NormalizedResponse(
            provider_kind=ProviderKind.OLLAMA,
            model_identifier="test",
            assistant_content="valid",
            prompt_token_count="10",  # type: ignore[arg-type]
        )
    # Valid int
    nr = NormalizedResponse(
        provider_kind=ProviderKind.OLLAMA,
        model_identifier="test",
        assistant_content="valid",
        prompt_token_count=10,
    )
    assert nr.prompt_token_count == 10
