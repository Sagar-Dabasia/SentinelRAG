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
            async with client.stream(**request_kwargs) as response:
                # 3xx, 4xx, 5xx treated as non-retryable
                if response.status_code >= 300:
                    raise ProviderHttpError(
                        provider,
                        f"HTTP {response.status_code} received.",
                        response.status_code,
                    )

                content_length_str = response.headers.get("Content-Length")
                if content_length_str:
                    try:
                        content_length = int(content_length_str)
                        if content_length > max_response_bytes:
                            msg = (
                                f"Response Content-Length {content_length} "
                                f"exceeds limit {max_response_bytes} bytes."
                            )
                            raise ResponseTooLargeError(provider, msg)
                    except ValueError:
                        pass

                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > max_response_bytes:
                        msg = (
                            "Response stream exceeded limit "
                            f"{max_response_bytes} bytes."
                        )
                        raise ResponseTooLargeError(provider, msg)

            # Reconstruct response to return it safely
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
            raise
        except httpx.RequestError as e:
            raise ProviderProtocolError(
                provider, f"Request failed: {type(e).__name__}"
            ) from e

    raise ProviderProtocolError(provider, "Maximum retries exceeded.")
