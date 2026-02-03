import pytest
import pytest_asyncio

from src.clients.redis_client import get_redis_client


@pytest_asyncio.fixture(scope="module")
async def redis_client():
    client = get_redis_client()
    await client.connect()

    yield client

    await client.close()


@pytest.mark.asyncio
async def test_redis_set_get(redis_client):
    await redis_client.redis.set("test_key", "test_value")
    value = await redis_client.redis.get("test_key")
    assert value == "test_value"

    await redis_client.redis.delete("test_key")
    value = await redis_client.redis.get("test_key")
    assert value is None
