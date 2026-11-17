from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import BaseError


class BotNotConfiguredError(BaseError):
    code: ClassVar[str] = "BOT_NOT_CONFIGURED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Бот не настроен"


class TelegramErrorError(BaseError):
    code: ClassVar[str] = "TELEGRAM_ERROR"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Ошибка Telegram"
