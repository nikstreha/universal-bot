from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class InvalidUploadMetadataError(DomainError):
    code: ClassVar[str] = "INVALID_METADATA"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Неверный размер файла"


class UploadInvalidStateError(DomainError):
    code: ClassVar[str] = "INVALID_STATE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Загрузка не принимает части"


class UploadExpiredError(DomainError):
    code: ClassVar[str] = "UPLOAD_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.GONE
    message_template: ClassVar[str] = "Срок загрузки истёк"


class UploadPartsMissingError(DomainError):
    code: ClassVar[str] = "PARTS_MISSING"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Не все части приняты"


class UploadAlreadyCompletedError(DomainError):
    code: ClassVar[str] = "ALREADY_COMPLETED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Файл уже сохранён"


class UploadStoppedError(DomainError):
    code: ClassVar[str] = "INVALID_STATE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Загрузка остановлена"
