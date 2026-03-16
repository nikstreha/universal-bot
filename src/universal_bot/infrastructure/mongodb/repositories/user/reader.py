from pymongo.asynchronous.database import AsyncDatabase

from src.universal_bot.application.port.db.repositories.user.reader import (
    IUserReader,
)
from universal_bot.infrastructure.mongodb.collections import Collections
from universal_bot.infrastructure.mongodb.documents.user import UserDocument


class UserReader(IUserReader):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.USER]

    async def get_by_id(self, user_id: int) -> UserDocument | None:
        doc = await self.collection.find_one({"_id": user_id})

        if not doc:
            return None

        return UserDocument.model_validate(doc)

    async def is_user_permitted(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocument(**doc).role.is_permitted()

        return False

    async def is_user_admin(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocument(**doc).role.is_admin()

        return False
