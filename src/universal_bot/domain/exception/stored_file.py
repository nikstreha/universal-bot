from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class StoredFileInvalidStateError(DomainError):
    code: ClassVar[str] = "INVALID_STATE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Файл удаляется"


class StoredFileRestoreExpiredError(DomainError):
    code: ClassVar[str] = "RESTORE_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.GONE
    message_template: ClassVar[str] = "Срок восстановления истёк"
