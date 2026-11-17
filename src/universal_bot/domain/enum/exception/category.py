from enum import StrEnum


class ErrorCategory(StrEnum):
    INTERNAL = "internal"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    GONE = "gone"
    INVALID_INPUT = "invalid_input"
    VALIDATION = "validation"
    RANGE = "range"
    TOO_LARGE = "too_large"
    RATE_LIMIT = "rate_limit"
    UNAVAILABLE = "unavailable"
    INSUFFICIENT_STORAGE = "insufficient_storage"
