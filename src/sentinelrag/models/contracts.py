from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from sentinelrag.config.settings import ProviderKind


class ChatRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: ChatRole
    content: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=131072),
    ]


class GenerationRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    seed: int | None = None

    def model_post_init(self, __context: Any) -> None:
        total_content = sum(len(m.content) for m in self.messages)
        if total_content > 524288:  # Half megabyte arbitrary limit
            raise ValueError("Total message content exceeds maximum allowed length.")


class NormalizedResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_kind: ProviderKind
    model_identifier: str
    assistant_content: str
    finish_reason: str | None = None
    prompt_token_count: int | None = None
    output_token_count: int | None = None


class ProviderAvailability(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    models: list[str]


# Base exception for all provider errors
class ProviderError(Exception):
    def __init__(
        self,
        provider: ProviderKind,
        category: str,
        message: str,
        retryable: bool,
        http_status: int | None = None,
    ) -> None:
        self.provider = provider
        self.category = category
        self.message = message
        self.retryable = retryable
        self.http_status = http_status
        super().__init__(f"[{provider.value}] {category}: {message}")


class ProviderDisabledError(ProviderError):
    def __init__(self, message: str = "Provider is disabled.") -> None:
        super().__init__(ProviderKind.DISABLED, "disabled", message, False)


class InvalidProviderConfigurationError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str) -> None:
        super().__init__(provider, "invalid_config", message, False)


class ProviderUnavailableError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str) -> None:
        super().__init__(provider, "unavailable", message, True)


class ProviderTimeoutError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str, retryable: bool) -> None:
        super().__init__(provider, "timeout", message, retryable)


class ProviderHttpError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str, status: int) -> None:
        # HTTP 4xx are not retryable. 5xx may be, but prompt says "Do not retry HTTP responses"  # noqa: E501
        # Wait, prompt says: "Do not retry HTTP 4xx responses, protocol errors, read timeouts or malformed responses."  # noqa: E501
        # And "Retry only httpx.ConnectError and httpx.ConnectTimeout."
        # So HTTP errors are NEVER retryable.
        super().__init__(provider, "http_error", message, False, status)


class ProviderProtocolError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str) -> None:
        super().__init__(provider, "protocol_error", message, False)


class ResponseTooLargeError(ProviderError):
    def __init__(self, provider: ProviderKind, message: str) -> None:
        super().__init__(provider, "response_too_large", message, False)


class ProviderClosedError(ProviderError):
    def __init__(self, provider: ProviderKind) -> None:
        super().__init__(
            provider, "provider_closed", "The provider is already closed.", False
        )
