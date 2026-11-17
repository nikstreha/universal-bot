from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class InvalidIdentifierError(DomainError):
    code: ClassVar[str] = "INVALID_IDENTIFIER"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Неверный идентификатор обновления"


class InvalidMetadataError(DomainError):
    code: ClassVar[str] = "INVALID_METADATA"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Неверный идентификатор установки"


class NotFoundError(DomainError):
    code: ClassVar[str] = "NOT_FOUND"
    category: ClassVar[ErrorCategory] = ErrorCategory.NOT_FOUND
    message_template: ClassVar[str] = "Загрузка не найдена"


class InvalidRangeError(DomainError):
    code: ClassVar[str] = "INVALID_RANGE"
    category: ClassVar[ErrorCategory] = ErrorCategory.INVALID_INPUT
    message_template: ClassVar[str] = "Неверный номер части"


class InvalidRequestError(DomainError):
    code: ClassVar[str] = "INVALID_REQUEST"
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
    message_template: ClassVar[str] = "Неверный размер страницы"


class RateLimitedError(DomainError):
    code: ClassVar[str] = "RATE_LIMITED"
    category: ClassVar[ErrorCategory] = ErrorCategory.RATE_LIMIT
    message_template: ClassVar[str] = "Слишком много попыток входа"


class InvalidStateError(DomainError):
    code: ClassVar[str] = "INVALID_STATE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Загрузка не принимает части"
