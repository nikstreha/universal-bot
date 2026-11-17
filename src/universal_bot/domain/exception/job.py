from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class JobAlreadyClaimedError(DomainError):
    code: ClassVar[str] = "LEASE_LOST"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Задача уже выполняется"


class JobLeaseLostError(DomainError):
    code: ClassVar[str] = "LEASE_LOST"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Задача передана другому обработчику"


class JobInvalidStateError(DomainError):
    code: ClassVar[str] = "INVALID_STATE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Задача не выполняется"


class LeaseLostError(DomainError):
    code: ClassVar[str] = "LEASE_LOST"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Задача не найдена"
