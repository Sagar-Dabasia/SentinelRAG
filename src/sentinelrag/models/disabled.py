from sentinelrag.models.contracts import (
    GenerationRequest,
    NormalizedResponse,
    ProviderAvailability,
    ProviderDisabledError,
)
from sentinelrag.models.provider import ModelProvider


class DisabledProvider(ModelProvider):
    def __init__(self) -> None:
        self._closed = False

    async def generate(self, request: GenerationRequest) -> NormalizedResponse:
        raise ProviderDisabledError()

    async def check_availability(self) -> ProviderAvailability:
        raise ProviderDisabledError()

    async def aclose(self) -> None:
        self._closed = True
