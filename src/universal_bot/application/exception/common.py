from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import BaseError


class ThumbnailNotReadyError(BaseError):
    code: ClassVar[str] = "THUMBNAIL_NOT_READY"
    category: ClassVar[ErrorCategory] = ErrorCategory.NOT_FOUND
    message_template: ClassVar[str] = "Миниатюра пока недоступна"


class RangeNotSatisfiableError(BaseError):
    code: ClassVar[str] = "RANGE_NOT_SATISFIABLE"
    category: ClassVar[ErrorCategory] = ErrorCategory.RANGE
    message_template: ClassVar[str] = "Диапазон вне файла"


class PartTooLargeError(BaseError):
    code: ClassVar[str] = "PART_TOO_LARGE"
    category: ClassVar[ErrorCategory] = ErrorCategory.TOO_LARGE
    message_template: ClassVar[str] = "Часть превышает размер"


class AuthRequiredError(BaseError):
    code: ClassVar[str] = "AUTH_REQUIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.AUTHENTICATION
    message_template: ClassVar[str] = "Войдите через Telegram"


class FileTooLargeError(BaseError):
    code: ClassVar[str] = "FILE_TOO_LARGE"
    category: ClassVar[ErrorCategory] = ErrorCategory.TOO_LARGE
    message_template: ClassVar[str] = "Размер файла превышает лимит"


class ThumbnailTooLargeError(BaseError):
    code: ClassVar[str] = "THUMBNAIL_TOO_LARGE"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Слишком большое разрешение изображения"


class UnsupportedPreviewError(BaseError):
    code: ClassVar[str] = "UNSUPPORTED_PREVIEW"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Предпросмотр этого контейнера не поддерживается"


class AccessRevokedError(BaseError):
    code: ClassVar[str] = "ACCESS_REVOKED"
    category: ClassVar[ErrorCategory] = ErrorCategory.PERMISSION
    message_template: ClassVar[str] = "Доступ пока не открыт"


class UploadCancelledError(BaseError):
    code: ClassVar[str] = "UPLOAD_CANCELLED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Загрузка остановлена"


class LimitReachedError(BaseError):
    code: ClassVar[str] = "LIMIT_REACHED"
    category: ClassVar[ErrorCategory] = ErrorCategory.RATE_LIMIT
    message_template: ClassVar[str] = "Слишком много незавершённых загрузок"


class AccessAlreadyGrantedError(BaseError):
    code: ClassVar[str] = "ACCESS_ALREADY_GRANTED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Доступ уже открыт"


class AdminProtectedError(BaseError):
    code: ClassVar[str] = "ADMIN_PROTECTED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Нельзя удалить администратора"


class InvalidUserIdError(BaseError):
    code: ClassVar[str] = "INVALID_USER_ID"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Неверный Telegram ID"


class PartConflictError(BaseError):
    code: ClassVar[str] = "PART_CONFLICT"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Часть содержит другие данные"


class IdempotencyConflictError(BaseError):
    code: ClassVar[str] = "IDEMPOTENCY_CONFLICT"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "Ключ уже использован для другого файла"


class AuthAttemptExpiredError(BaseError):
    code: ClassVar[str] = "AUTH_ATTEMPT_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.GONE
    message_template: ClassVar[str] = "Войдите через Telegram ещё раз"


class NotWhitelistedError(BaseError):
    code: ClassVar[str] = "NOT_WHITELISTED"
    category: ClassVar[ErrorCategory] = ErrorCategory.PERMISSION
    message_template: ClassVar[str] = "Доступ пока не открыт"


class LoginNotConfiguredError(BaseError):
    code: ClassVar[str] = "LOGIN_NOT_CONFIGURED"
    category: ClassVar[ErrorCategory] = ErrorCategory.UNAVAILABLE
    message_template: ClassVar[str] = "Вход через бота ещё не настроен"


class UploadExpiredError(BaseError):
    code: ClassVar[str] = "UPLOAD_EXPIRED"
    category: ClassVar[ErrorCategory] = ErrorCategory.GONE
    message_template: ClassVar[str] = "Срок загрузки истёк"
