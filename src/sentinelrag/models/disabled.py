from sentinelrag.config.settings import ProviderKind
from sentinelrag.models.contracts import (
    GenerationRequest,
    NormalizedResponse,
    ProviderAvailability,
    ProviderClosedError,
    ProviderDisabledError,
)
from sentinelrag.models.provider import ModelProvider


class DisabledProvider(ModelProvider):
    def __init__(self) -> None:
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise ProviderClosedError(ProviderKind.DISABLED)

    async def generate(self, request: GenerationRequest) -> NormalizedResponse:
        self._ensure_open()
        raise ProviderDisabledError()

    async def check_availability(self) -> ProviderAvailability:
        self._ensure_open()
        raise ProviderDisabledError()

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
