from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.port.db.repositories.chat.writer import IChatWriter
from universal_bot.domain.entity.chat import Chat
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.infrastructure.mongodb.collections import Collections
from universal_bot.infrastructure.mongodb.documents.chat import ChatDocument
from universal_bot.infrastructure.mongodb.mapper.chat import ChatMapper


class ChatWriter(IChatWriter):
    def __init__(self, db: AsyncDatabase) -> None:
        self._chats = db[Collections.CHAT]
        self._buckets = db[Collections.MESSAGE_BUCKET]

    async def get_by_id(self, chat_id: ChatId) -> Chat | None:
        doc = await self._chats.find_one({"_id": chat_id.value})
        if not doc:
            return None
        return ChatMapper.to_entity(ChatDocument.model_validate(doc))

    async def create(self, chat: Chat) -> None:
        doc = ChatMapper.to_document(chat).model_dump(by_alias=True)
        await self._chats.insert_one(doc)

    async def delete(self, chat_id: ChatId) -> None:
        await self._buckets.delete_many({"chat_id": chat_id.value})
        await self._chats.delete_one({"_id": chat_id.value})
