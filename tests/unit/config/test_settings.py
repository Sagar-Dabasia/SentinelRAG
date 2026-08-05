import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from sentinelrag.config.settings import ProviderKind, SentinelSettings


def test_default_provider_is_disabled() -> None:
    settings = SentinelSettings()
    assert settings.provider == ProviderKind.DISABLED
    assert settings.endpoint is None
    assert settings.model_identifier is None


def test_enabled_provider_requires_endpoint_and_model() -> None:
    with pytest.raises(ValidationError, match="Endpoint is required"):
        SentinelSettings(provider=ProviderKind.OLLAMA, model_identifier="model")

    with pytest.raises(ValidationError, match="Model identifier is required"):
        SentinelSettings(provider=ProviderKind.OLLAMA, endpoint="http://127.0.0.1/api")  # type: ignore[arg-type]


def test_disabled_provider_rejects_stale_values() -> None:
    with pytest.raises(
        ValidationError, match="Endpoint must be absent when provider is disabled"
    ):
        SentinelSettings(
            provider=ProviderKind.DISABLED,
            endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
        )

    with pytest.raises(
        ValidationError,
        match="Model identifier must be absent when provider is disabled",
    ):
        SentinelSettings(provider=ProviderKind.DISABLED, model_identifier="model")


def test_loopback_host_acceptance() -> None:
    s1 = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    assert s1.endpoint and s1.endpoint.host == "127.0.0.1"

    s2 = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://localhost/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    assert s2.endpoint and s2.endpoint.host == "localhost"

    s3 = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://[::1]/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    assert s3.endpoint and s3.endpoint.host == "[::1]"

    s4 = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.0.0.2/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    assert s4.endpoint and s4.endpoint.host == "127.0.0.2"

    s5 = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.255.255.254/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    assert s5.endpoint and s5.endpoint.host == "127.255.255.254"


def test_public_host_rejection() -> None:
    with pytest.raises(ValidationError, match="Endpoint host is invalid") as exc_info:
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://example.com/api",  # type: ignore[arg-type]
            model_identifier="test",
        )
    assert "example.com" not in str(exc_info.value)


def test_lan_address_rejection() -> None:
    with pytest.raises(ValidationError, match="Only loopback hosts are allowed"):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://192.168.1.100/api",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_zero_address_rejection() -> None:
    with pytest.raises(ValidationError, match="Only loopback hosts are allowed"):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://0.0.0.0/api",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_url_credential_rejection() -> None:
    with pytest.raises(ValidationError, match="Credentials in URL are rejected"):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://user:pass@127.0.0.1/api",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_query_fragment_rejection() -> None:
    with pytest.raises(
        ValidationError, match="Query strings and fragments are rejected"
    ):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://127.0.0.1/api?query=1",  # type: ignore[arg-type]
            model_identifier="test",
        )
    with pytest.raises(
        ValidationError, match="Query strings and fragments are rejected"
    ):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://127.0.0.1/api#fragment",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_wrong_ollama_path_rejection() -> None:
    with pytest.raises(
        ValidationError, match="Ollama base path must resolve exactly to /api"
    ):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://127.0.0.1/v1",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_wrong_lm_studio_path_rejection() -> None:
    with pytest.raises(
        ValidationError, match="LM Studio base path must resolve exactly to /v1"
    ):
        SentinelSettings(
            provider=ProviderKind.LM_STUDIO,
            endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
            model_identifier="test",
        )


def test_timeout_bounds() -> None:
    with pytest.raises(ValidationError):
        SentinelSettings(connect_timeout=0.0)
    with pytest.raises(ValidationError):
        SentinelSettings(read_timeout=1000.0)


def test_retry_bounds() -> None:
    with pytest.raises(ValidationError):
        SentinelSettings(retry_limit=-1)
    with pytest.raises(ValidationError):
        SentinelSettings(retry_limit=3)


def test_output_limits() -> None:
    with pytest.raises(ValidationError):
        SentinelSettings(max_requested_output_tokens=0)
    with pytest.raises(ValidationError):
        SentinelSettings(max_response_characters=0)


def test_invalid_model_identifier() -> None:
    with pytest.raises(ValidationError):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
            model_identifier="",
        )
    with pytest.raises(ValidationError):
        SentinelSettings(
            provider=ProviderKind.OLLAMA,
            endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
            model_identifier="a" * 129,
        )


def test_environment_prefix_loading() -> None:
    with patch.dict(
        os.environ,
        {
            "SENTINELRAG_PROVIDER": "ollama",
            "SENTINELRAG_ENDPOINT": "http://127.0.0.1/api",
            "SENTINELRAG_MODEL_IDENTIFIER": "env-model",
        },
    ):
        settings = SentinelSettings()
        assert settings.provider == ProviderKind.OLLAMA
        assert settings.endpoint and str(settings.endpoint) == "http://127.0.0.1/api"
        assert settings.model_identifier == "env-model"


def test_settings_representations_do_not_expose_secret_values() -> None:
    settings = SentinelSettings()
    rep = repr(settings)
    assert (
        "password" not in rep.lower()
    )  # though we have no passwords, ensure representation is safe


def test_misspelled_environment_variable_ignored() -> None:
    with patch.dict(
        os.environ,
        {
            "SENTINELRAG_PROVIDER": "ollama",
            "SENTINELRAG_ENDPOINT": "http://127.0.0.1/api",
            "SENTINELRAG_MODEL_IDENTIFIER": "env-model",
            "SENTINELRAG_TYPO_SETTING": "value",
        },
    ):
        # Pydantic Settings ignores misspelled environment variables
        # even when extra="forbid" is set, as env vars are not passed to __init__.
        settings = SentinelSettings()
        assert not hasattr(settings, "typo_setting")
        assert not hasattr(settings, "SENTINELRAG_TYPO_SETTING")
