from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class InvalidTelegramUserIdError(DomainError):
    code: ClassVar[str] = "INVALID_USER_ID"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Неверный Telegram ID"
