from pymongo.asynchronous.database import AsyncDatabase

from src.universal_bot.application.port.db.repositories.chat.writer import IMyChatWriter
from universal_bot.domain.entity.chat import MyChat
from universal_bot.domain.value_object.message.message import Message
from universal_bot.domain.value_object.user.id import UserId
from universal_bot.infrastructure.mongodb.collections import Collections
from universal_bot.infrastructure.mongodb.mapper.chat import ChatMapper
from universal_bot.infrastructure.mongodb.mapper.message import MessageMapper


class MyChatWriter(IMyChatWriter):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.CHATS]

    async def replace(self, chat: MyChat) -> None:
        doc = ChatMapper.to_document(chat).model_dump()

        await self.collection.replace_one(
            {"_id": doc["_id"]},
            doc,
            upsert=True,
        )

    async def add_message(
        self,
        user_id: UserId,
        message: Message,
    ) -> None:
        message_doc = MessageMapper.to_document(message).model_dump

        await self.collection.update_one(
            {"user_id": user_id.value},
            {
                "$push": {"messages": message_doc},
                "$set": {"updated_at": message.created_at},
            },
        )

    async def create(self, chat: MyChat) -> None:
        doc = ChatMapper.to_document(chat).model_dump()

        await self.collection.insert_one(doc)
