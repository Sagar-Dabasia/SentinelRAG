from typing import Protocol

from sentinelrag.models.contracts import (
    GenerationRequest,
    NormalizedResponse,
    ProviderAvailability,
)


class ModelProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> NormalizedResponse:
        """Generate a response for the given request."""
        ...

    async def check_availability(self) -> ProviderAvailability:
        """Check provider availability and return available models."""
        ...

    async def aclose(self) -> None:
        """Close the underlying client. Repeated calls must be safe."""
        ...
