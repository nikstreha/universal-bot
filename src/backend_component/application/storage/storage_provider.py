import logging
from abc import ABC, abstractmethod
from typing import BinaryIO

from src.backend_component.application.dto.ai_chat.content_types import ContentTypes
from src.backend_component.application.dto.storage.delete_file import DeleteFileDTO
from src.backend_component.application.dto.storage.get_file import DownloadDTO, GetPersignedUrlDTO
from src.backend_component.application.dto.storage.put_file import PutFileDTO

logger = logging.getLogger(__name__)


class IStorageProvider(ABC):
    @abstractmethod
    async def check_or_create_bucket(self, bucket_name: str) -> None: ...
    
    @abstractmethod
    async def upload_file(self, file: PutFileDTO) -> None: ...

    @abstractmethod
    async def download_file(self, download_object: DownloadDTO) -> bytes:
        ...
    
    @abstractmethod
    async def delete_file(self, file: DeleteFileDTO) -> None: ...

    @abstractmethod
    async def get_presigned_url(self, presigned_url: GetPersignedUrlDTO) -> str: ...
