from typing import Any

import httpx

from sentinelrag.config.settings import ProviderKind, SentinelSettings
from sentinelrag.models.contracts import (
    ProviderHttpError,
    ProviderProtocolError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResponseTooLargeError,
)


def create_http_client(
    settings: SentinelSettings, transport: httpx.AsyncBaseTransport | None = None
) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        connect=settings.connect_timeout,
        read=settings.read_timeout,
        write=settings.write_timeout,
        pool=settings.pool_timeout,
    )
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)

    # trust_env=False and follow_redirects=False are mandatory
    return httpx.AsyncClient(
        base_url=str(settings.endpoint) if settings.endpoint else "",
        timeout=timeout,
        limits=limits,
        trust_env=False,
        follow_redirects=False,
        transport=transport,
    )


async def execute_request_with_retries(
    client: httpx.AsyncClient,
    request_kwargs: dict[str, Any],
    provider: ProviderKind,
    retry_limit: int,
    max_response_bytes: int,
) -> httpx.Response:
    attempts = 0
    max_attempts = retry_limit + 1

    while attempts < max_attempts:
        attempts += 1
        try:
            # We enforce max_response_bytes by streaming or checking content-length,
            # but httpx doesn't support a simple max_bytes flag directly on request().
            # However, for simplicity and since we don't want to stream every request
            # if we can just read it (we can't easily stream and retry safely without
            # writing a lot of code), we will do a normal request, but we will check
            # the Content-Length header first. If it's too large, we reject it.
            # Then we read. If the body is larger than max_response_bytes, we reject it.

            # The prompt says: "If the provider supplies a content length exceeding the configured byte limit, fail before parsing where possible."  # noqa: E501
            # We can use client.stream()
            async with client.stream(**request_kwargs) as response:
                content_length_str = response.headers.get("Content-Length")
                if content_length_str:
                    try:
                        content_length = int(content_length_str)
                        if content_length > max_response_bytes:
                            raise ResponseTooLargeError(
                                provider,
                                f"Response Content-Length {content_length} exceeds limit {max_response_bytes} bytes.",  # noqa: E501
                            )
                    except ValueError:
                        pass

                # Check HTTP status
                if response.status_code >= 400:
                    await response.aread()  # Read error body but don't expose it
                    raise ProviderHttpError(
                        provider,
                        f"HTTP {response.status_code} received.",
                        response.status_code,
                    )

                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > max_response_bytes:
                        raise ResponseTooLargeError(
                            provider,
                            f"Response stream exceeded limit {max_response_bytes} bytes.",  # noqa: E501
                        )

                # Now build a normal response object with the body we read
                response.read()  # ensures it's marked as read

                # httpx stream leaves response unread in a way, we'll just parse the json from the bytes.  # noqa: E501
                pass

            # Reconstruct response to return it easily
            res = httpx.Response(
                status_code=response.status_code,
                headers=response.headers,
                content=bytes(body),
                request=response.request,
            )
            return res

        except httpx.ConnectTimeout as e:
            if attempts >= max_attempts:
                raise ProviderTimeoutError(
                    provider, "Connection timed out.", retryable=True
                ) from e
            continue
        except httpx.ConnectError as e:
            if attempts >= max_attempts:
                raise ProviderUnavailableError(
                    provider, "Failed to connect to provider."
                ) from e
            continue
        except httpx.ReadTimeout as e:
            # Read timeouts are not retryable
            raise ProviderTimeoutError(
                provider, "Read timed out.", retryable=False
            ) from e
        except httpx.WriteTimeout as e:
            raise ProviderTimeoutError(
                provider, "Write timed out.", retryable=False
            ) from e
        except httpx.PoolTimeout as e:
            raise ProviderTimeoutError(
                provider, "Pool timed out.", retryable=False
            ) from e
        except ProviderHttpError, ResponseTooLargeError:
            # Pass these through without retry
            raise
        except httpx.RequestError as e:
            # Protocol or other errors
            raise ProviderProtocolError(
                provider, f"Request failed: {type(e).__name__}"
            ) from e

    # Should not be reached
    raise ProviderProtocolError(provider, "Maximum retries exceeded.")
