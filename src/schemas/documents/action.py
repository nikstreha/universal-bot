from enum import Enum


class Actions(str, Enum):
    MEDIA_UPLOAD = "media_upload"
    MEDIA_DOWNLOAD = "media_download"
    TRANSCRIPTION = "transcription"
    OTHER = "other"
