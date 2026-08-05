import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from sentinelrag.config.settings import ProviderKind
from sentinelrag.models.contracts import (
    ProviderHttpError,
    ProviderProtocolError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResponseTooLargeError,
)
from sentinelrag.models.http import execute_request_with_retries


class MockStreamResponse:
    def __init__(
        self, status_code: int, headers: dict[str, str], content: bytes
    ) -> None:
        self.status_code = status_code
        self.headers = httpx.Headers(headers)
        self.content = content
        self.request = httpx.Request("POST", "http://test")

    async def __aenter__(self) -> MockStreamResponse:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    async def aread(self) -> None:
        pass

    async def aiter_bytes(self) -> AsyncGenerator[bytes]:
        chunk_size = 2
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i : i + chunk_size]

    def read(self) -> None:
        pass


def test_execute_request_with_retries_success() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()
        with patch.object(
            client, "stream", return_value=MockStreamResponse(200, {}, b'{"ok": true}')
        ):
            resp = await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=1000,
            )
            assert resp.status_code == 200
            assert resp.content == b'{"ok": true}'

    asyncio.run(_run())


def test_execute_request_with_retries_http_error() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()
        with (
            patch.object(
                client, "stream", return_value=MockStreamResponse(400, {}, b"Bad")
            ),
            pytest.raises(ProviderHttpError, match="HTTP 400"),
        ):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=1000,
            )

    asyncio.run(_run())


def test_execute_request_with_retries_content_length_limit() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()
        with (
            patch.object(
                client,
                "stream",
                return_value=MockStreamResponse(200, {"Content-Length": "2000"}, b"x"),
            ),
            pytest.raises(ResponseTooLargeError, match="exceeds limit 1000"),
        ):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=1000,
            )

    asyncio.run(_run())


def test_execute_request_with_retries_streaming_limit() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()
        with (
            patch.object(
                client, "stream", return_value=MockStreamResponse(200, {}, b"123456")
            ),
            pytest.raises(ResponseTooLargeError, match="exceeded limit 5"),
        ):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=5,
            )

    asyncio.run(_run())


def test_execute_request_with_retries_connect_error() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()

        def raise_connect_error(*args: Any, **kwargs: Any) -> httpx.Response:
            raise httpx.ConnectError("Connection failed")

        with patch.object(
            client, "stream", side_effect=raise_connect_error
        ) as mock_stream:
            with pytest.raises(ProviderUnavailableError):
                await execute_request_with_retries(
                    client=client,
                    request_kwargs={"method": "POST", "url": "http://test"},
                    provider=ProviderKind.OLLAMA,
                    retry_limit=1,
                    max_response_bytes=1000,
                )
            assert mock_stream.call_count == 2

    asyncio.run(_run())


def test_execute_request_with_retries_read_timeout() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()

        def raise_read_timeout(*args: Any, **kwargs: Any) -> httpx.Response:
            raise httpx.ReadTimeout("Read failed")

        with patch.object(
            client, "stream", side_effect=raise_read_timeout
        ) as mock_stream:
            with pytest.raises(ProviderTimeoutError, match="Read timed out"):
                await execute_request_with_retries(
                    client=client,
                    request_kwargs={"method": "POST", "url": "http://test"},
                    provider=ProviderKind.OLLAMA,
                    retry_limit=1,
                    max_response_bytes=1000,
                )
            assert mock_stream.call_count == 1

    asyncio.run(_run())


def test_execute_request_with_retries_protocol_error() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()

        def raise_protocol_error(*args: Any, **kwargs: Any) -> httpx.Response:
            raise httpx.ProtocolError("Protocol error")

        with patch.object(
            client, "stream", side_effect=raise_protocol_error
        ) as mock_stream:
            with pytest.raises(ProviderProtocolError):
                await execute_request_with_retries(
                    client=client,
                    request_kwargs={"method": "POST", "url": "http://test"},
                    provider=ProviderKind.OLLAMA,
                    retry_limit=1,
                    max_response_bytes=1000,
                )
            assert mock_stream.call_count == 1

    asyncio.run(_run())
