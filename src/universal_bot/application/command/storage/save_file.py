import asyncio
import logging

from universal_bot.application.dto.storage.file import FileDTO
from universal_bot.application.dto.storage.put_file import PutFileDTO
from universal_bot.application.dto.storage.response import (
    SaveFileErrorResponseDTO,
    SaveFilesResponseDTO,
    Status,
)
from universal_bot.application.port.storage.storage_provider import IStorageProvider
from universal_bot.application.port.storage.upload_limiter import IUploadLimiter
from universal_bot.composition.configuration.config import Settings

logger = logging.getLogger(__name__)


class SaveFileInteractor:
    def __init__(
        self,
        storage_provider: IStorageProvider,
        upload_limiter: IUploadLimiter,
        configuration: Settings,
    ):
        self._storage_provider = storage_provider
        self._configuration = configuration
        self._upload_limiter = upload_limiter

    async def __call__(self, file_collection: list[FileDTO]) -> SaveFilesResponseDTO:
        async with self._upload_limiter.acquire():
            results = await asyncio.gather(
                *[self._save_file(file) for file in file_collection],
                )
        errors: list = [r for r in results if r is not None]

        if not errors:
            return SaveFilesResponseDTO(status=Status.SUCCESS)
        elif len(errors) == len(file_collection):
            return SaveFilesResponseDTO(status=Status.FAIL, errors=errors)
        else:
            return SaveFilesResponseDTO(status=Status.PARTIAL_SUCCESS, errors=errors)

    async def _save_file(self, file: FileDTO) -> SaveFileErrorResponseDTO | None:
        try:
            res = await self._storage_provider.upload_file(
                    PutFileDTO(
                        bucket_name=self._configuration.MINIO_BUCKET,
                        object_name=file.file_name,
                        data=file.data,
                        content_type=file.content_type,
                    )
                )

            if not res:
                return SaveFileErrorResponseDTO(file_name=file.file_name)
        
        except Exception as e:
            logger.error("Error uploading file %s: %s", file.file_name, e)
            return SaveFileErrorResponseDTO(file_name=file.file_name, message="Unexpected error!!!")
