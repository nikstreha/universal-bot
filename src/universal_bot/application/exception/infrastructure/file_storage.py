from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import BaseError


class StoredObjectUnavailableError(BaseError):
    code: ClassVar[str] = "STORAGE_OBJECT_UNAVAILABLE"
    category: ClassVar[ErrorCategory] = ErrorCategory.UNAVAILABLE
    message_template: ClassVar[str] = "Сохранённый объект недоступен для чтения"


class StorageUnavailableError(BaseError):
    code: ClassVar[str] = "STORAGE_UNAVAILABLE"
    category: ClassVar[ErrorCategory] = ErrorCategory.UNAVAILABLE
    message_template: ClassVar[str] = "Хранилище временно недоступно"


class StorageFullError(BaseError):
    code: ClassVar[str] = "STORAGE_FULL"
    category: ClassVar[ErrorCategory] = ErrorCategory.INSUFFICIENT_STORAGE
    message_template: ClassVar[str] = "Недостаточно места на сервере"


class StoragePolicyUnsafeError(BaseError):
    code: ClassVar[str] = "STORAGE_POLICY_UNSAFE"
    category: ClassVar[ErrorCategory] = ErrorCategory.UNAVAILABLE
    message_template: ClassVar[str] = (
        "Bucket должен быть приватным, без публичной bucket policy"
    )
