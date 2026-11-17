from enum import StrEnum


class UploadState(StrEnum):
    RECEIVING = "receiving"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"
