from beanie import init_beanie
from pymongo import AsyncMongoClient
from src.core.config import settings
from src.schemas.documents.chat import Chat


async def init_mongo() -> None:
    client = AsyncMongoClient(settings.mongo_url)

    db = client[settings.MONGO_DB_NAME]

    await init_beanie(database=db, document_models=[Chat])
