from collections.abc import Callable
from functools import wraps

import urllib3
from minio.error import S3Error

from universal_bot.application.exception.infrastructure.file_storage import (
    StorageUnavailableError,
    StoredObjectUnavailableError,
)


def storage_operation[**P, T](operation: Callable[P, T]) -> Callable[P, T]:
    @wraps(operation)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return operation(*args, **kwargs)
        except S3Error as exc:
            if exc.code in ("NoSuchKey", "NoSuchObject"):
                raise StoredObjectUnavailableError() from exc
            raise StorageUnavailableError() from exc
        except (urllib3.exceptions.HTTPError, OSError) as exc:
            raise StorageUnavailableError() from exc

    return wrapped
