import logging
from typing import BinaryIO, Optional

from miniopy_async import Minio
from src.core.config import settings
from src.schemas.content_types import ContentTypes

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )

        logger.info("Minio client initialized")

    async def check_or_create_bucket(self, bucket_name: str):
        if not await self.client.bucket_exists(bucket_name):
            await self.client.make_bucket(bucket_name)
            logger.info("Bucket %s created", bucket_name)
        logger.info("Bucket %s exists", bucket_name)

    async def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            data: BinaryIO,
            content_type: ContentTypes
            ):
        await self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=len(data),
            content_type=content_type.value,
            )
        
        logger.info("File %s uploaded to bucket %s", object_name, bucket_name)

    async def download_file(self, bucket_name: str, object_name: str):
        async with await self.client.get_object(
            bucket_name=bucket_name,
            object_name=object_name,
        ) as obj:
            data = await obj.read()

        logger.info("File %s downloaded from bucket %s", object_name, bucket_name)

        return data


_minio_client: Optional[MinioClient] = None

def get_minio_client() -> MinioClient:
    global _minio_client
    if _minio_client is None:
        _minio_client = MinioClient()
    return _minio_client
