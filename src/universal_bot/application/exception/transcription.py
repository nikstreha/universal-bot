from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import BaseError


class AudioUnavailableError(BaseError):
    code: ClassVar[str] = "AUDIO_UNAVAILABLE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Telegram не вернул файл"


class AudioTooLongError(BaseError):
    code: ClassVar[str] = "AUDIO_TOO_LONG"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Аудио слишком длинное"
