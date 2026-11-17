from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class SessionRevokedError(DomainError):
    code: ClassVar[str] = "SESSION_REVOKED"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Сессия отозвана"


class SessionExpiredError(DomainError):
    code: ClassVar[str] = "SESSION_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Войдите через Telegram ещё раз"
