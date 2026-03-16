from dataclasses import dataclass


@dataclass(frozen=True)
class DownloadDTO:
    bucket_name: str
    object_name: str


@dataclass(frozen=True)
class GetPersignedUrlDTO:
    bucket_name: str
    object_name: str
    expires: int = 3600