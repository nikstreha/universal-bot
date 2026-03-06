from pymongo.asynchronous.database import AsyncDatabase

from backend_component.domain.entity.chat import MyChat
from backend_component.domain.value_object.message.message import Message
from backend_component.domain.value_object.user.id import UserId
from backend_component.infrastructure.mongodb.collections import Collections
from backend_component.infrastructure.mongodb.mapper.chat import ChatMapper
from backend_component.infrastructure.mongodb.mapper.message import MessageMapper


class MyChatWriter:
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
                "$push": {
                    "messages": message_doc
                },
                "$set": {
                    "updated_at": message.created_at
                }
            }
        )

    async def create(self, chat: MyChat) -> None:
        doc = ChatMapper.to_document(chat).model_dump()

        await self.collection.insert_one(doc)
