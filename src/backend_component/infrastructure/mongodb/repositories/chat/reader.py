from pymongo.asynchronous.database import AsyncDatabase
from backend_component.infrastructure.mongodb.collections import Collections
from backend_component.infrastructure.mongodb.models.chat import ChatDocument
from backend_component.infrastructure.mongodb.models.message import MessageDocument


class MyChatReader:
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.CHATS]

    async def get_by_user_id(self, user_id: str) -> ChatDocument | None:
        doc = await self.collection.find_one({"user.user_id": user_id})

        if not doc:
            return None

        return ChatDocument.model_validate(doc)

    async def get_messages(self, user_id: str, limit: int = 20) -> list[MessageDocument]:
        doc = await self.collection.find_one(
            {"user_id": user_id},
            {"messages": {"$slice": -limit}},
        )

        if not doc:
            return []

        return [MessageDocument.model_validate(msg) for msg in doc["messages"]]
