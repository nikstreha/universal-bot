from universal_bot.application.dto.storage.file import FileDTO
from universal_bot.application.dto.storage.put_file import PutFileDTO
from universal_bot.application.dto.storage.responce import (
    SaveFileErrorResponceDTO,
    SaveFilesResponceDTO,
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

    async def __call__(self, file_collention: list[FileDTO]) -> SaveFilesResponceDTO:
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
                errors.append(SaveFileErrorResponceDTO(file_name=file.file_name))

        if not errors:
            return SaveFilesResponceDTO(status=Status.SUCCESS)
        elif len(errors) == len(file_collention):
            return SaveFilesResponceDTO(status=Status.FAIL, errors=errors)
        else:
            return SaveFilesResponceDTO(status=Status.PARTIAL_SUCCESS, errors=errors)
