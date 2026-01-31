import pytest

from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from unittest.mock import AsyncMock, PropertyMock, patch

from src.core.config import settings
from src.clients.redis_client import RedisClient


@pytest.mark.asyncio
async def test_redis_connect_success():
    client = RedisClient()
    await client.connect()

    assert client.redis is not None

    pong = await client.redis.ping()
    assert pong is True

    await client.close()
    assert client.redis is None


@pytest.mark.asyncio
async def test_redis_set_get():
    client = RedisClient()
    await client.connect()

    await client.redis.set("test_key", "test_value")
    value = await client.redis.get("test_key")
    assert value == "test_value"

    await client.redis.delete("test_key")
    value = await client.redis.get("test_key")
    assert value is None

    await client.close()
