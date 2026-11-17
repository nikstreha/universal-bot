from enum import StrEnum


class ThumbnailState(StrEnum):
    PENDING = "pending"
    READY = "ready"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"
