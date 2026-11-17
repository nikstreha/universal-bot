from enum import StrEnum


class TelegramUpdateState(StrEnum):
    QUEUED = "queued"
    COMPLETED = "completed"
