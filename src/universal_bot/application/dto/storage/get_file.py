from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class DownloadDTO:
    bucket_name: str
    object_name: str


@dataclass(frozen=True)
class GetPresignedUrlDTO:
    bucket_name: str
    object_name: str
    expires: timedelta = timedelta(hours=12)


@dataclass(frozen=True)
class GetFilesFromDirectoryDTO:
    bucket_name: str
    prefix: str
    limit: int = 10
    offset_name: str | None = None


@dataclass(frozen=True)
class FolderDTO:
    name: str
    path: str


@dataclass(frozen=True)
class ItemDTO:
    name: str
    url: str


@dataclass(frozen=True)
class GetFilesFromDirectoryResponseDTO:
    folders: list[FolderDTO]
    items: list[ItemDTO]
    has_more: bool
    last_processed_key: str | None = None
