from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class InvalidFileNameError(DomainError):
    code: ClassVar[str] = "INVALID_METADATA"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Недопустимое имя файла"


class InvalidSHA256DigestError(DomainError):
    code: ClassVar[str] = "INVALID_METADATA"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Неверный SHA-256 файла"


class ChecksumMismatchError(DomainError):
    code: ClassVar[str] = "CHECKSUM_MISMATCH"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Хеш части не совпадает"


class FileTrashedError(DomainError):
    code: ClassVar[str] = "FILE_TRASHED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Передача остановлена"
