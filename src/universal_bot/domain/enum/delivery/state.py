from enum import StrEnum


class DeliveryState(StrEnum):
    QUEUED = "queued"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
