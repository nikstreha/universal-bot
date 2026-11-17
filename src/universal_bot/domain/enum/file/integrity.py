from enum import StrEnum


class FileIntegrity(StrEnum):
    VERIFIED = "verified"
    CORRUPT = "corrupt"
    UNAVAILABLE = "unavailable"
    MISSING = "missing"
