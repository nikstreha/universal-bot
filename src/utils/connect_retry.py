import asyncio
import logging
import random
from functools import wraps
from typing import TypeVar, Callable, Awaitable, ParamSpec

import aiohttp
from src.core.config import settings

T = TypeVar("T")
P = ParamSpec("P")

logger = logging.getLogger(__name__)

def _full_jitter(attempt: int) -> float:
    max_delay = settings.CONNECT_BACKOFF_BASE * (2 ** attempt)
    return random.uniform(0, max_delay)


def retry_with_reconnect(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
        last_exc: Exception | None = None

        for attempt_op in range(settings.OPERATION_RETRIES):
            try:
                return await asyncio.wait_for(
                    func(self, *args, **kwargs),
                    timeout=settings.OPERATION_TIMEOUT,
                )

            except asyncio.TimeoutError as exc:
                last_exc = exc
                logger.error(
                    "Operation timeout (%s/%s) for %s",
                    attempt_op + 1,
                    settings.OPERATION_RETRIES,
                    func.__name__,
                )

            except (aiohttp.client_exceptions.ClientConnectorError, ConnectionRefusedError) as exc:
                last_exc = exc
                logger.error("Connection error during %s, trying to reconnect", func.__name__)

                for attempt_conn in range(settings.CONNECT_RETRIES):
                    try:
                        await asyncio.wait_for(
                            self.connect(),
                            timeout=settings.CONNECT_TIMEOUT,
                        )
                        break
                    except (aiohttp.client_exceptions.ClientConnectorError, ConnectionRefusedError) as exc_conn:
                        last_exc = exc_conn
                        if attempt_conn == settings.CONNECT_RETRIES - 1:
                            break
                        delay = _full_jitter(attempt_conn)
                        logger.error(
                            "Reconnect failed (%s/%s). Retrying in %.2fs",
                            attempt_conn + 1,
                            settings.CONNECT_RETRIES,
                            delay,
                        )
                        await asyncio.sleep(delay)

            except Exception:
                raise

        raise last_exc

    return wrapper
