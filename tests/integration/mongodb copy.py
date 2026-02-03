import pytest_asyncio
import pytest
from pymongo import AsyncMongoClient

from beanie import init_beanie

from src.schemas.message_roles import MessageRoles
from src.core.config import settings

from src.schemas.documents.chat import Chat
from src.schemas.user import UserBaseSchema
from src.schemas.db_chat import DBHistorySchema


@pytest_asyncio.fixture
async def beanie_db():
    client = AsyncMongoClient(settings.mongo_url)
    db = client["test_db"]

    await init_beanie(database=db, document_models=[Chat])

    yield

    await client.drop_database("test_db")
    client.close()


@pytest.mark.asyncio
async def test_create_for_user(beanie_db):
    user = UserBaseSchema(
        user_id=123,
        username="test_user",
        role=MessageRoles.USER,
    )

    chat = await Chat.create_for_user(user)

    assert chat is not None
    assert chat.user.user_id == 123
    assert chat.user.username == "test_user"


@pytest.mark.asyncio
async def test_from_user(beanie_db):

    found = await Chat.from_user(user_id=123)

    assert found is not None
    assert found.user.user_id == 123
    assert found.user.username == "test_user"