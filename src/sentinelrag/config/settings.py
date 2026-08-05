import ipaddress
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import (
    AnyHttpUrl,
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderKind(StrEnum):
    DISABLED = "disabled"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"


class SentinelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTINELRAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    provider: ProviderKind = ProviderKind.DISABLED
    endpoint: AnyHttpUrl | None = None
    model_identifier: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=128,
            pattern=r"^[^\x00-\x1F]*$",
        ),
    ] = None

    connect_timeout: float = Field(default=5.0, ge=0.1, le=60.0)
    read_timeout: float = Field(default=30.0, ge=0.1, le=300.0)
    write_timeout: float = Field(default=10.0, ge=0.1, le=60.0)
    pool_timeout: float = Field(default=5.0, ge=0.1, le=60.0)

    retry_limit: int = Field(default=1, ge=0, le=2)

    max_requested_output_tokens: int = Field(default=1024, ge=1, le=4096)
    max_response_characters: int = Field(default=32768, ge=1, le=1048576)
    max_response_bytes: int = Field(default=131072, ge=1, le=4194304)

    @model_validator(mode="after")
    def validate_provider_requirements(self) -> SentinelSettings:
        if self.provider == ProviderKind.DISABLED:
            if self.endpoint is not None:
                raise ValueError("Endpoint must be absent when provider is disabled.")
            if self.model_identifier is not None:
                raise ValueError(
                    "Model identifier must be absent when provider is disabled."
                )
        else:
            if self.endpoint is None:
                raise ValueError(
                    f"Endpoint is required when provider is {self.provider.value}."
                )
            if self.model_identifier is None:
                msg = (
                    "Model identifier is required when provider is "
                    f"{self.provider.value}."
                )
                raise ValueError(msg)

            # Validate endpoint host and path
            host = self.endpoint.host
            if not host:
                raise ValueError("Endpoint host is missing.")

            # IPv6 cleanup for pydantic
            raw_host = host.strip("[]")

            if raw_host != "localhost":
                try:
                    ip = ipaddress.ip_address(raw_host)
                    if not ip.is_loopback:
                        raise ValueError(
                            f"Only loopback hosts are allowed. Rejected host: {host}"
                        )
                except ValueError as e:
                    msg = (
                        f"Only loopback hosts are allowed. Invalid host format: {host}"
                    )
                    raise ValueError(msg) from e

            if self.endpoint.username or self.endpoint.password:
                raise ValueError("Credentials in URL are rejected.")

            if self.endpoint.query or self.endpoint.fragment:
                raise ValueError("Query strings and fragments are rejected.")

            path = self.endpoint.path or ""
            if self.provider == ProviderKind.OLLAMA and path != "/api":
                raise ValueError("Ollama base path must resolve exactly to /api.")
            if self.provider == ProviderKind.LM_STUDIO and path != "/v1":
                raise ValueError("LM Studio base path must resolve exactly to /v1.")

        return self

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint_scheme(
        cls, v: AnyHttpUrl | None, info: ValidationInfo
    ) -> AnyHttpUrl | None:
        if v is not None and v.scheme != "http":
            raise ValueError("Only http is accepted for endpoints in Phase 1B.")
        return v
