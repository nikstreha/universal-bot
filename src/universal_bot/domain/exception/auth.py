from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class LoginRequiredError(DomainError):
    code: ClassVar[str] = "LOGIN_REQUIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.PERMISSION
    message_template: ClassVar[str] = "Подтвердите аккаунт в боте"


class LoginCancelledError(DomainError):
    code: ClassVar[str] = "LOGIN_CANCELLED"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Вход отменён"


class InvalidLoginError(DomainError):
    code: ClassVar[str] = "INVALID_LOGIN"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Подтвердите вход со своего аккаунта"
