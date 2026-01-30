import pytest
from unittest.mock import AsyncMock, patch

from src.clients.minio_client import MinioClient
from src.schemas.content_types import ContentTypes

@pytest.fixture
def minio_client():
    with patch('src.clients.minio_client.Minio'):
        return MinioClient()

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exists, should_create",
    [
        (True, False),
        (False, True),
    ]
)
async def test_check_or_create_bucket(
    minio_client,
    exists,
    should_create
):
    with patch.object(
        minio_client.client,
        "bucket_exists",
        new_callable=AsyncMock,
        return_value=exists,
    ) as mock_exists, patch.object(
        minio_client.client,
        "make_bucket",
        new_callable=AsyncMock,
    ) as mock_make:

        await minio_client.check_or_create_bucket("test-bucket")

        mock_exists.assert_called_once_with("test-bucket")

        if should_create:
            mock_make.assert_called_once_with("test-bucket")
        else:
            mock_make.assert_not_called()

@pytest.mark.asyncio
async def test_upload_file(minio_client):
    with patch.object(minio_client.client, 'put_object', new_callable=AsyncMock) as mock_fput:
        bucket = "test-bucket"
        obj = "test-object"
        data = b"test-data"
        content_type = ContentTypes.PNG
        
        
        await minio_client.upload_file(bucket, obj, data, content_type)

        args, kwargs = mock_fput.call_args
        
        assert kwargs["bucket_name"] == bucket
        assert kwargs["object_name"] == obj
        assert kwargs["length"] == len(data)
        assert kwargs["content_type"] == "image/png"

@pytest.mark.asyncio
async def test_download_file(minio_client):
    with patch.object(minio_client.client, 'get_object', new_callable=AsyncMock) as mock_fget:
        bucket = "test-bucket"
        obj = "test-object"

        mock_stream = AsyncMock()
        mock_stream.read.return_value = b"file-data"

        mock_fget.return_value.__aenter__.return_value = mock_stream
        mock_fget.return_value.__aexit__.return_value = None

        result = await minio_client.download_file(bucket, obj)

        assert result == b"file-data"
