from enum import StrEnum


class JobKind(StrEnum):
    FINALIZE = "finalize"
    VERIFY = "verify"
    THUMBNAIL = "thumbnail"
    TRANSCRIBE = "transcribe"
