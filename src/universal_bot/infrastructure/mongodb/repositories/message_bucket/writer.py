import logging

from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.port.db.repositories.message_bucket.writer import (
    IMessageBucketWriter,
)
from universal_bot.domain.entity.message_bucket import MessageBucket
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.message.message import Message
from universal_bot.domain.value_object.message_bucket.seq import BucketSeq
from universal_bot.infrastructure.mongodb.collections import Collections
from universal_bot.infrastructure.mongodb.documents.message_bucket import (
    MessageBucketDocument,
)
from universal_bot.infrastructure.mongodb.mapper.message import MessageMapper
from universal_bot.infrastructure.mongodb.mapper.message_bucket import (
    MessageBucketMapper,
)

logger = logging.getLogger(__name__)


class MessageBucketWriter(IMessageBucketWriter):
    def __init__(self, db: AsyncDatabase, bucket_size: int) -> None:
        self._collection = db[Collections.MESSAGE_BUCKET]
        self._bucket_size = bucket_size

    async def get_latest_bucket(self, chat_id: ChatId) -> MessageBucket | None:
        doc = await self._collection.find_one(
            {"chat_id": chat_id.value},
            sort=[("seq", DESCENDING)],
        )
        if not doc:
            return None
        return MessageBucketMapper.to_entity(MessageBucketDocument.model_validate(doc))

    async def add_message(self, chat_id: ChatId, message: Message) -> None:
        message_doc = MessageMapper.to_document(message).model_dump(by_alias=True)
        latest = await self.get_latest_bucket(chat_id)

        if latest and not latest.is_full(self._bucket_size):
            result = await self._collection.update_one(
                {"_id": latest.id_.value, "count": {"$lt": self._bucket_size}},
                {
                    "$push": {"messages": message_doc},
                    "$inc": {"count": 1},
                    "$set": {"updated_at": message.created_at},
                },
            )
            if result.matched_count > 0:
                return

        next_seq = BucketSeq(latest.seq.value + 1) if latest else BucketSeq(0)
        new_bucket = MessageBucket.create(
            chat_id=chat_id,
            seq=next_seq,
            message=message,
        )
        doc = MessageBucketMapper.to_document(new_bucket)
        await self._collection.insert_one(doc.model_dump(by_alias=True))

    async def delete_by_chat_id(self, chat_id: ChatId) -> None:
        await self._collection.delete_many({"chat_id": chat_id.value})
