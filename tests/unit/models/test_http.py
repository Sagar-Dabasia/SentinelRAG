import asyncio
from collections.abc import AsyncIterator

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


class MockAsyncByteStream(httpx.AsyncByteStream):
    def __init__(self, content: bytes, chunk_size: int = 2) -> None:
        self._content = content
        self._chunk_size = chunk_size
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for i in range(0, len(self._content), self._chunk_size):
            yield self._content[i : i + self._chunk_size]

    async def aclose(self) -> None:
        self.closed = True


# 1. Successful bounded streamed response
def test_1_successful_stream() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"hello")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        resp = await execute_request_with_retries(
            client=client,
            request_kwargs={"method": "POST", "url": "http://test"},
            provider=ProviderKind.OLLAMA,
            retry_limit=1,
            max_response_bytes=100,
        )
        assert resp.content == b"hello"
        assert stream.closed

    asyncio.run(_run())


# 2. Content-Length exactly at limit
def test_2_content_length_exact() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"12345")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, headers={"Content-Length": "5"}, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        resp = await execute_request_with_retries(
            client=client,
            request_kwargs={"method": "POST", "url": "http://test"},
            provider=ProviderKind.OLLAMA,
            retry_limit=1,
            max_response_bytes=5,
        )
        assert resp.content == b"12345"
        assert stream.closed

    asyncio.run(_run())


# 3. Content-Length over limit
def test_3_content_length_over() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"123456")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, headers={"Content-Length": "6"}, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ResponseTooLargeError, match="exceeds limit 5"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=5,
            )
        assert stream.closed

    asyncio.run(_run())


# 4. Negative Content-Length
def test_4_negative_content_length() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"data")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, headers={"Content-Length": "-1"}, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderProtocolError, match="negative"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=100,
            )
        assert stream.closed

    asyncio.run(_run())


# 5. Non-numeric Content-Length
def test_5_non_numeric_content_length() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"data")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, headers={"Content-Length": "abc"}, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderProtocolError, match="non-numeric"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=100,
            )
        assert stream.closed

    asyncio.run(_run())


# 6. Chunked response exactly at limit
def test_6_chunked_exact() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"12345", chunk_size=1)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        resp = await execute_request_with_retries(
            client=client,
            request_kwargs={"method": "POST", "url": "http://test"},
            provider=ProviderKind.OLLAMA,
            retry_limit=1,
            max_response_bytes=5,
        )
        assert resp.content == b"12345"
        assert stream.closed

    asyncio.run(_run())


# 7. Chunked response over limit
def test_7_chunked_over() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"123456", chunk_size=1)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ResponseTooLargeError, match="exceeded limit 5"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=5,
            )
        assert stream.closed

    asyncio.run(_run())


# 8. HTTP 300/301/307 without redirect following
def test_8_http_3xx_no_redirect() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"redirect")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(301, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderHttpError, match="HTTP 301"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=100,
            )
        assert stream.closed

    asyncio.run(_run())


# 9. HTTP 400 no retry
def test_9_http_400() -> None:
    async def _run() -> None:
        calls = 0
        stream = MockAsyncByteStream(b"bad request body error hidden secret")

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(400, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderHttpError) as exc_info:
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=3,
                max_response_bytes=100,
            )
        assert calls == 1
        assert "HTTP 400" in str(exc_info.value)
        assert stream.closed

    asyncio.run(_run())


# 10. HTTP 500 no retry
def test_10_http_500() -> None:
    async def _run() -> None:
        calls = 0
        stream = MockAsyncByteStream(b"server error body")

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(500, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderHttpError) as exc_info:
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=2,
                max_response_bytes=100,
            )
        assert calls == 1
        assert "HTTP 500" in str(exc_info.value)
        assert stream.closed

    asyncio.run(_run())


# 11. Error body never appears in exception text
def test_11_error_body_hidden() -> None:
    async def _run() -> None:
        secret_body = b"SECRET_ERROR_PAYLOAD"
        stream = MockAsyncByteStream(secret_body)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(403, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderHttpError) as exc_info:
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=100,
            )
        assert "SECRET_ERROR_PAYLOAD" not in str(exc_info.value)
        assert stream.closed

    asyncio.run(_run())


# 12. ConnectError exact attempt count
def test_12_connect_error_retries() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.ConnectError("cannot connect")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderUnavailableError):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=3,
                max_response_bytes=100,
            )
        assert calls == 4

    asyncio.run(_run())


# 13. ConnectTimeout exact attempt count
def test_13_connect_timeout_retries() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.ConnectTimeout("timeout")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderTimeoutError):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=2,
                max_response_bytes=100,
            )
        assert calls == 3

    asyncio.run(_run())


# 14. ReadTimeout one attempt
def test_14_read_timeout_no_retry() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.ReadTimeout("read timeout")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderTimeoutError, match="Read timed out"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=5,
                max_response_bytes=100,
            )
        assert calls == 1

    asyncio.run(_run())


# 15. WriteTimeout one attempt
def test_15_write_timeout_no_retry() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.WriteTimeout("write timeout")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderTimeoutError, match="Write timed out"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=5,
                max_response_bytes=100,
            )
        assert calls == 1

    asyncio.run(_run())


# 16. PoolTimeout one attempt
def test_16_pool_timeout_no_retry() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.PoolTimeout("pool timeout")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderTimeoutError, match="Pool timed out"):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=5,
                max_response_bytes=100,
            )
        assert calls == 1

    asyncio.run(_run())


# 17. RemoteProtocolError one attempt
def test_17_remote_protocol_error_no_retry() -> None:
    async def _run() -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            raise httpx.RemoteProtocolError("protocol err")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderProtocolError):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=5,
                max_response_bytes=100,
            )
        assert calls == 1

    asyncio.run(_run())


# 18. Stream closes after success (Tested in test_1_successful_stream)
# 19. Stream closes after response-size failure (Tested in test_3 and test_7)
# 20. Stream closes after protocol failure (Tested in test_4, test_5)
# Extra stream closure check
def test_stream_closes_on_http_error() -> None:
    async def _run() -> None:
        stream = MockAsyncByteStream(b"bad")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, stream=stream)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)

        with pytest.raises(ProviderHttpError):
            await execute_request_with_retries(
                client=client,
                request_kwargs={"method": "POST", "url": "http://test"},
                provider=ProviderKind.OLLAMA,
                retry_limit=1,
                max_response_bytes=100,
            )
        assert stream.closed

    asyncio.run(_run())
