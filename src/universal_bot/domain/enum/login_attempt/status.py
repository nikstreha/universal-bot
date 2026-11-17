from enum import StrEnum


class LoginAttemptStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    DENIED = "denied"
    CANCELLED = "cancelled"
