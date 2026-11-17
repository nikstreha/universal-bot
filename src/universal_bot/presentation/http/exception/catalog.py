from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import BaseError


class ErrorCatalog:
    _statuses: ClassVar[dict[ErrorCategory, int]] = {
        ErrorCategory.INTERNAL: 500,
        ErrorCategory.AUTHENTICATION: 401,
        ErrorCategory.PERMISSION: 403,
        ErrorCategory.NOT_FOUND: 404,
        ErrorCategory.CONFLICT: 409,
        ErrorCategory.GONE: 410,
        ErrorCategory.INVALID_INPUT: 400,
        ErrorCategory.VALIDATION: 422,
        ErrorCategory.RANGE: 416,
        ErrorCategory.TOO_LARGE: 413,
        ErrorCategory.RATE_LIMIT: 429,
        ErrorCategory.UNAVAILABLE: 503,
        ErrorCategory.INSUFFICIENT_STORAGE: 507,
    }

    @classmethod
    def status_for(cls, error: BaseError) -> int:
        return cls._statuses[error.category]
