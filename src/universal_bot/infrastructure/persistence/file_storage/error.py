from collections.abc import Awaitable, Callable
from functools import wraps

from aiohttp import ClientError as HTTPClientError
from botocore.exceptions import BotoCoreError, ClientError

from universal_bot.application.exception.infrastructure.file_storage import (
    StorageUnavailableError,
    StoredObjectUnavailableError,
)


def storage_operation[**P, T](
    operation: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    @wraps(operation)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await operation(*args, **kwargs)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "NoSuchObject") or (
                code in ("404", "NotFound")
                and operation.__name__ in ("read", "size", "download", "inspect")
            ):
                raise StoredObjectUnavailableError() from exc
            raise StorageUnavailableError() from exc
        except (BotoCoreError, HTTPClientError, OSError) as exc:
            raise StorageUnavailableError() from exc

    return wrapped
