from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.dto.ai_chat.documents import (
    ChatDocumentDTO,
    MessageDocumentDTO,
)
from universal_bot.application.port.db.repositories.chat.reader import IMyChatReader
from universal_bot.infrastructure.mongodb.collections import Collections


class MyChatReader(IMyChatReader):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.CHATS]

    async def get_by_user_id(self, user_id: int) -> ChatDocumentDTO | None:
        doc = await self.collection.find_one({"user_id": user_id})

        if not doc:
            return None

        return ChatDocumentDTO.model_validate(doc)

    async def get_messages(
        self, user_id: int, limit: int = 20
    ) -> list[MessageDocumentDTO]:
        doc = await self.collection.find_one(
            {"user_id": user_id},
            {"messages": {"$slice": -limit}},
        )

        if not doc:
            return []

        return [MessageDocumentDTO.model_validate(msg) for msg in doc["messages"]]
