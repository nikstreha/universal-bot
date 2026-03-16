import logging
from types import TracebackType

from miniopy_async import Minio
from backend_component.application.dto.storage.delete_file import DeleteFileDTO
from backend_component.application.dto.storage.put_file import PutFileDTO
from backend_component.application.dto.storage.get_file import DownloadDTO, GetPersignedUrlDTO
from backend_component.application.storage.storage_provider import IStorageProvider

logger = logging.getLogger(__name__)


class MinioProvider(IStorageProvider):
    def __init__(self, endpoint: str, user: str, password: str) -> None:
        self.client: Minio | None = None
        self.endpoint = endpoint
        self.access_key = user
        self.secret_key = password

    async def up(self) -> None:
        if self.client is not None:
            return
        
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

        logger.info("Minio client initialized")

    async def down(self) -> None:
        if not self.client:
            return
        
        self.client.close_session()
        logger.info("Minio client closed")

    async def check_or_create_bucket(self, bucket_name: str) -> None:
        if not await self.client.bucket_exists(bucket_name):
            await self.client.make_bucket(bucket_name)
            logger.info("Bucket %s created", bucket_name)
        else:
            logger.info("Bucket %s already exists", bucket_name)

    async def upload_file(self, file: PutFileDTO) -> None:
        await self.client.put_object(
            bucket_name=file.bucket_name,
            object_name=file.object_name,
            data=file.data,
            length=-1,
            content_type=file.content_type.value,
        )

        logger.debug("File %s uploaded to bucket %s", file.object_name, file.bucket_name)

    async def download_file(self, download_object: DownloadDTO) -> bytes:
        async with await self.client.get_object(
            bucket_name=download_object.bucket_name,
            object_name=download_object.object_name,
        ) as obj:
            data = await obj.read()

        logger.debug(
            "File %s downloaded from bucket %s",
            download_object.object_name,
            download_object.bucket_name,
        )

        return data
    
    async def delete_file(self, file: DeleteFileDTO) -> None:
        await self.client.remove_object(file.bucket_name, file.object_name)

        logger.debug("File %s deleted from bucket %s", file.object_name, file.bucket_name)

    async def get_presigned_url(self, presigned_url: GetPersignedUrlDTO) -> str:
        return await self.client.presigned_get_object(
            bucket_name=presigned_url.bucket_name,
            object_name=presigned_url.object_name,
            expires=presigned_url.expires,
        )

    async def __aenter__(self) -> MinioProvider:
        await self.up()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.down()
