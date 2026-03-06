from pymongo.asynchronous.database import AsyncDatabase
from backend_component.infrastructure.mongodb.collections import Collections
from backend_component.infrastructure.mongodb.models.chat import ChatDocument
from backend_component.infrastructure.mongodb.models.user import UserDocument


class UserReader:
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.USER]

    async def get_by_id(self, user_id: str) -> ChatDocument | None:
        doc = await self.collection.find_one({"_id": user_id})

        if not doc:
            return None

        return UserDocument.model_validate(doc)

    async def is_user_permitted(self, user_id: str) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocument(**doc).role.is_permitted()

        return False

    async def is_user_admin(self, user_id: str) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocument(**doc).role.is_admin()

        return False
    