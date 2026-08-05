import asyncio

import pytest

from sentinelrag.models.contracts import (
    ChatMessage,
    ChatRole,
    GenerationRequest,
    ProviderDisabledError,
)
from sentinelrag.models.disabled import DisabledProvider


def test_disabled_provider_generate_raises() -> None:
    async def _run() -> None:
        provider = DisabledProvider()
        req = GenerationRequest(
            messages=[ChatMessage(role=ChatRole.USER, content="Hello")]
        )
        with pytest.raises(ProviderDisabledError):
            await provider.generate(req)

    asyncio.run(_run())


def test_disabled_provider_check_availability_raises() -> None:
    async def _run() -> None:
        provider = DisabledProvider()
        with pytest.raises(ProviderDisabledError):
            await provider.check_availability()

    asyncio.run(_run())


def test_disabled_provider_aclose() -> None:
    async def _run() -> None:
        provider = DisabledProvider()
        await provider.aclose()
        assert provider._closed

    asyncio.run(_run())
