from universal_bot.application.dto.storage.file import FileDTO
from universal_bot.application.dto.storage.put_file import PutFileDTO
from universal_bot.application.dto.storage.response import (
    SaveFileErrorResponseDTO,
    SaveFilesResponseDTO,
    Status,
)
from universal_bot.application.port.storage.storage_provider import IStorageProvider
from universal_bot.composition.configuration.config import Settings


class SaveFileInteractor:
    def __init__(
        self,
        storage_provider: IStorageProvider,
        configuration: Settings,
    ):
        self._storage_provider = storage_provider
        self._configuration = configuration

    async def __call__(self, file_collention: list[FileDTO]) -> SaveFilesResponseDTO:
        errors = []

        for file in file_collention:
            res = await self._storage_provider.upload_file(
                PutFileDTO(
                    bucket_name=self._configuration.MINIO_BUCKET,
                    object_name=file.file_name,
                    data=file.data,
                    content_type=file.content_type,
                )
            )

            if not res:
                errors.append(SaveFileErrorResponseDTO(file_name=file.file_name))

        if not errors:
            return SaveFilesResponseDTO(status=Status.SUCCESS)
        elif len(errors) == len(file_collention):
            return SaveFilesResponseDTO(status=Status.FAIL, errors=errors)
        else:
            return SaveFilesResponseDTO(status=Status.PARTIAL_SUCCESS, errors=errors)
