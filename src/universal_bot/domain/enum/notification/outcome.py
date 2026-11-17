from enum import StrEnum


class LoginOutcome(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
