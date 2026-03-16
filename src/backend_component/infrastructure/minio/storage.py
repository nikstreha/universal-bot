import logging
from types import TracebackType
from typing import BinaryIO

from miniopy_async import Minio
from backend_component.composition.configuration.config import settings
from src.backend_component.application.dto.ai_chat.content_types import ContentTypes

logger = logging.getLogger(__name__)


class MinioProvider:
    def __init__(self) -> None:
        self.client: Minio | None = None

    async def up(self) -> None:
        if self.client is not None:
            return
        
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )

        logger.info("Minio client initialized")

    async def check_or_create_bucket(self, bucket_name: str) -> None:
        if not await self.client.bucket_exists(bucket_name):
            await self.client.make_bucket(bucket_name)
            logger.info("Bucket %s created", bucket_name)
        else:
            logger.info("Bucket %s already exists", bucket_name)

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        data: BinaryIO,
        content_type: ContentTypes,
    ) -> None:
        await self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=-1,
            content_type=content_type.value,
        )

        logger.info("File %s uploaded to bucket %s", object_name, bucket_name)

    async def download_file(self, bucket_name: str, object_name: str) -> bytes:
        async with await self.client.get_object(
            bucket_name=bucket_name,
            object_name=object_name,
        ) as obj:
            data = await obj.read()

        logger.info(
            "File %s downloaded from bucket %s", object_name, bucket_name,
        )

        return data
    
    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        await self.client.remove_object(bucket_name, object_name)

        logger.info("File %s deleted from bucket %s", object_name, bucket_name)

    async def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        return await self.client.presigned_get_object(
            bucket_name,
            object_name,
            expires=expires,
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
        pass