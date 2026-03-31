from abc import ABC, abstractmethod

from universal_bot.application.dto.storage.delete_file import DeleteFileDTO
from universal_bot.application.dto.storage.get_file import (
    DownloadDTO,
    GetFilesFromDirectoryDTO,
    GetFilesFromDirectoryResponseDTO,
    GetPresignedUrlDTO,
)
from universal_bot.application.dto.storage.put_file import PutFileDTO


class IStorageProvider(ABC):
    @abstractmethod
    async def check_or_create_bucket(self, bucket_name: str) -> None: ...

    @abstractmethod
    async def upload_file(self, file: PutFileDTO) -> bool: ...

    @abstractmethod
    async def download_file(self, download_object: DownloadDTO) -> bytes: ...

    @abstractmethod
    async def delete_file(self, file: DeleteFileDTO) -> None: ...

    @abstractmethod
    async def get_presigned_url(self, presigned_url: GetPresignedUrlDTO) -> str: ...

    @abstractmethod
    async def get_files_from_directory(
        self, files_request: GetFilesFromDirectoryDTO
    ) -> GetFilesFromDirectoryResponseDTO: ...
