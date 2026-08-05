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
    match settings.provider:
        case ProviderKind.DISABLED:
            return DisabledProvider()
        case ProviderKind.OLLAMA:
            return OllamaAdapter(settings, transport)
        case ProviderKind.LM_STUDIO:
            return LMStudioAdapter(settings, transport)
