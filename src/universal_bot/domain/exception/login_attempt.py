from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class LoginAttemptExpiredError(DomainError):
    code: ClassVar[str] = "AUTH_ATTEMPT_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.GONE
    message_template: ClassVar[str] = "Попытка входа истекла"


class LoginAttemptOwnerMismatchError(DomainError):
    code: ClassVar[str] = "INVALID_LOGIN"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Попытка принадлежит другому аккаунту"
