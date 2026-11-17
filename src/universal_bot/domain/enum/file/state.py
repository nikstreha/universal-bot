from enum import StrEnum


class FileState(StrEnum):
    ACTIVE = "active"
    TRASHED = "trashed"
    PURGING = "purging"
