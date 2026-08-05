import httpx

from sentinelrag.config.settings import ProviderKind, SentinelSettings
from sentinelrag.models.disabled import DisabledProvider
from sentinelrag.models.lm_studio import LMStudioAdapter
from sentinelrag.models.ollama import OllamaAdapter
from sentinelrag.models.provider import ModelProvider


def create_provider(
    settings: SentinelSettings,
    transport: httpx.AsyncBaseTransport | None = None,
) -> ModelProvider:
    if settings.provider == ProviderKind.DISABLED:
        return DisabledProvider()
    elif settings.provider == ProviderKind.OLLAMA:
        return OllamaAdapter(settings, transport)
    elif settings.provider == ProviderKind.LM_STUDIO:
        return LMStudioAdapter(settings, transport)

    # Should be unreachable because settings validation rejects unknown providers
    raise ValueError(f"Unsupported provider: {settings.provider}")
