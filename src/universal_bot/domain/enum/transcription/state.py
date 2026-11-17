from enum import StrEnum


class TranscriptionState(StrEnum):
    ACCEPTED = "accepted"
    TRANSCRIBING = "transcribing"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
