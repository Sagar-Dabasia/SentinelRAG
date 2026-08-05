from sentinelrag.config.settings import ProviderKind, SentinelSettings
from sentinelrag.models.disabled import DisabledProvider
from sentinelrag.models.factory import create_provider
from sentinelrag.models.lm_studio import LMStudioAdapter
from sentinelrag.models.ollama import OllamaAdapter


def test_create_disabled_provider() -> None:
    settings = SentinelSettings(provider=ProviderKind.DISABLED)
    provider = create_provider(settings)
    assert isinstance(provider, DisabledProvider)


def test_create_ollama_provider() -> None:
    settings = SentinelSettings(
        provider=ProviderKind.OLLAMA,
        endpoint="http://127.0.0.1/api",  # type: ignore[arg-type]
        model_identifier="test",
    )
    provider = create_provider(settings)
    assert isinstance(provider, OllamaAdapter)


def test_create_lm_studio_provider() -> None:
    settings = SentinelSettings(
        provider=ProviderKind.LM_STUDIO,
        endpoint="http://127.0.0.1/v1",  # type: ignore[arg-type]
        model_identifier="test",
    )
    provider = create_provider(settings)
    assert isinstance(provider, LMStudioAdapter)


def test_create_unknown_provider() -> None:
    settings = SentinelSettings(provider=ProviderKind.DISABLED)
    # Force an invalid value to test the unreachable fallback
    settings.provider = "unknown"  # type: ignore[assignment]
    import pytest

    with pytest.raises(ValueError, match="Unsupported provider: unknown"):
        create_provider(settings)
