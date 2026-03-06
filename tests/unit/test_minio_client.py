import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend_component.infrastructure.minio.minio_client import get_minio_client
from backend_component.application.dto.content_types import ContentTypes


@pytest.fixture(scope="module")
def minio_client():
    with patch("src.clients.minio_client.Minio") as mock_minio:
        mock_instance = MagicMock()
        mock_instance.bucket_exists = AsyncMock()
        mock_instance.make_bucket = AsyncMock()
        mock_instance.put_object = AsyncMock()
        mock_instance.get_object = AsyncMock()

        mock_minio.return_value = mock_instance

        client = get_minio_client()
        client.client = mock_instance

        return client


@pytest.mark.asyncio
async def test_check_or_create_bucket_existing_bucket(minio_client):
    with (
        patch.object(
            minio_client.client,
            "bucket_exists",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch.object(
            minio_client.client,
            "make_bucket",
            new_callable=AsyncMock,
        ),
    ):
        await minio_client.check_or_create_bucket("test-bucket")


@pytest.mark.asyncio
async def test_check_or_create_bucket_creates_bucket(minio_client):
    with (
        patch.object(
            minio_client.client,
            "bucket_exists",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch.object(
            minio_client.client,
            "make_bucket",
            new_callable=AsyncMock,
        ) as mock_make,
    ):
        await minio_client.check_or_create_bucket("test-bucket")

        mock_make.assert_called_once_with("test-bucket")


@pytest.mark.asyncio
async def test_check_or_create_bucket_bucket_exists_fails(minio_client):
    with patch.object(
        minio_client.client,
        "bucket_exists",
        new_callable=AsyncMock,
        side_effect=RuntimeError("minio unavailable"),
    ):
        with pytest.raises(RuntimeError, match="minio unavailable"):
            await minio_client.check_or_create_bucket("test-bucket")


@pytest.mark.asyncio
async def test_check_or_create_bucket_make_bucket_fails(minio_client, caplog):
    with (
        patch.object(
            minio_client.client,
            "bucket_exists",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch.object(
            minio_client.client,
            "make_bucket",
            new_callable=AsyncMock,
            side_effect=RuntimeError("create failed"),
        ),
    ):
        with pytest.raises(RuntimeError):
            await minio_client.check_or_create_bucket("test-bucket")


@pytest.mark.asyncio
async def test_upload_file_success(minio_client):
    with patch.object(
        minio_client.client,
        "put_object",
        new_callable=AsyncMock,
    ):
        await minio_client.upload_file(
            bucket_name="test-bucket",
            object_name="test-object",
            data=b"file-data",
            content_type=ContentTypes.PNG,
        )


@pytest.mark.asyncio
async def test_upload_file_put_object_fails(minio_client):
    with patch.object(
        minio_client.client,
        "put_object",
        new_callable=AsyncMock,
        side_effect=RuntimeError("upload failed"),
    ):
        with pytest.raises(RuntimeError, match="upload failed"):
            await minio_client.upload_file(
                bucket_name="test-bucket",
                object_name="test-object",
                data=b"file-data",
                content_type=ContentTypes.PNG,
            )


@pytest.mark.asyncio
async def test_download_file_success(minio_client):
    with patch.object(
        minio_client.client,
        "get_object",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_stream = AsyncMock()
        mock_stream.read.return_value = b"file-data"

        mock_get.return_value.__aenter__.return_value = mock_stream
        mock_get.return_value.__aexit__.return_value = None

        result = await minio_client.download_file("test-bucket", "test-object")

        assert result == b"file-data"


@pytest.mark.asyncio
async def test_download_file_empty_stream(minio_client):
    with patch.object(
        minio_client.client,
        "get_object",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_stream = AsyncMock()
        mock_stream.read.return_value = b""

        mock_get.return_value.__aenter__.return_value = mock_stream
        mock_get.return_value.__aexit__.return_value = None

        result = await minio_client.download_file("test-bucket", "test-object")

        assert result == b""


@pytest.mark.asyncio
async def test_download_file_get_object_fails(minio_client):
    with patch.object(
        minio_client.client,
        "get_object",
        new_callable=AsyncMock,
        side_effect=RuntimeError("download failed"),
    ):
        with pytest.raises(RuntimeError, match="download failed"):
            await minio_client.download_file("test-bucket", "test-object")
