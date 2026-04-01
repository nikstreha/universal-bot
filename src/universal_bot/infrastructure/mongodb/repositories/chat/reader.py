from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.dto.ai_chat.chat_list import (
    GetChatsByUserIdRequestDTO,
    GetChatsByTgChatIdRequestDTO,
    GetChatsResponseDTO,
)
from universal_bot.application.dto.ai_chat.documents import ChatDocumentDTO
from universal_bot.application.port.db.repositories.chat.reader import IChatReader
from universal_bot.infrastructure.mongodb.collections import Collections


class ChatReader(IChatReader):
    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db[Collections.CHAT]

    async def get_by_id(self, chat_id: int) -> ChatDocumentDTO | None:
        doc = await self._collection.find_one({"_id": chat_id})
        if not doc:
            return None
        return ChatDocumentDTO.model_validate(doc)

    async def get_by_user_id(
        self, request: GetChatsByUserIdRequestDTO
    ) -> GetChatsResponseDTO:
        query: dict = {"user_id": request.user_id}

        if request.after_id is not None:
            query["_id"] = {"$gt": request.after_id}

        docs = (
            await self._collection.find(query)
            .sort("_id", 1)
            .limit(request.limit + 1)
            .to_list(length=request.limit + 1)
        )

        after_id: int | None = None
        if len(docs) > request.limit:
            after_id = docs[-1]["_id"]
            docs.pop()

        return GetChatsResponseDTO(
            chats=[ChatDocumentDTO.model_validate(doc) for doc in docs],
            after_id=after_id,
        )
    
    async def get_by_tg_chat_id(
        self, request: GetChatsByTgChatIdRequestDTO
    ) -> GetChatsResponseDTO:
        query: dict = {"tg_chat_id": request.tg_chat_id}

        if request.after_id is not None:
            query["_id"] = {"$gt": request.after_id}

        docs = (
            await self._collection.find(query)
            .sort("_id", 1)
            .limit(request.limit + 1)
            .to_list(length=request.limit + 1)
        )

        after_id: int | None = None
        if len(docs) > request.limit:
            after_id = docs[-1]["_id"]
            docs.pop()

        return GetChatsResponseDTO(
            chats=[ChatDocumentDTO.model_validate(doc) for doc in docs],
            after_id=after_id,
        )
