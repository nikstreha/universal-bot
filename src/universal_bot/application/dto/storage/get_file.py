from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class DownloadDTO:
    bucket_name: str
    object_name: str


@dataclass(frozen=True)
class GetPersignedUrlDTO:
    bucket_name: str
    object_name: str
    expires: timedelta = timedelta(hours=12)
