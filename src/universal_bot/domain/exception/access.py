from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class AdminConfigurationMismatchError(DomainError):
    code: ClassVar[str] = "ADMIN_CONFIGURATION_MISMATCH"
    category: ClassVar[ErrorCategory] = ErrorCategory.UNAVAILABLE
    message_template: ClassVar[str] = "Администратор ещё не зарегистрирован"


class AdminRequiredError(DomainError):
    code: ClassVar[str] = "ADMIN_REQUIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.PERMISSION
    message_template: ClassVar[str] = "Недостаточно прав"
