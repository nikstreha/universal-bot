from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.dto.ai_chat.bucket import MessageBucketDTO
from universal_bot.application.dto.ai_chat.documents import MessageDocumentDTO
from universal_bot.application.dto.ai_chat.message_page import (
    GetMessagesRequestDTO,
    GetMessagesResponseDTO,
    MessageCursor,
)
from universal_bot.application.port.db.repositories.message_bucket.reader import (
    IMessageBucketReader,
)
from universal_bot.infrastructure.mongodb.collections import Collections


class MessageBucketReader(IMessageBucketReader):
    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db[Collections.MESSAGE_BUCKET]

    async def get_messages(
        self, request: GetMessagesRequestDTO
    ) -> GetMessagesResponseDTO:
        query: dict = {"chat_id": request.chat_id}

        if request.cursor:
            query["seq"] = {"$lte": request.cursor.seq}

        buckets = (
            await self._collection.find(query)
            .sort("seq", DESCENDING)
            .to_list(length=None)
        )

        messages: list[MessageDocumentDTO] = []
        next_cursor: MessageCursor | None = None

        for bucket in buckets:
            bucket_msgs: list[dict] = bucket["messages"]
            seq: int = bucket["seq"]

            end = len(bucket_msgs)
            if request.cursor and seq == request.cursor.seq:
                end = request.cursor.index

            for i in range(end - 1, -1, -1):
                if len(messages) >= request.limit:
                    next_cursor = MessageCursor(seq=seq, index=i + 1)
                    break
                messages.append(MessageDocumentDTO.model_validate(bucket_msgs[i]))

            if next_cursor:
                break

        messages.reverse()

        return GetMessagesResponseDTO(
            messages=messages,
            next_cursor=next_cursor,
        )

    async def get_buckets_by_chat(self, chat_id: int) -> list[MessageBucketDTO]:
        docs = (
            await self._collection.find({"chat_id": chat_id})
            .sort("seq", DESCENDING)
            .to_list(length=None)
        )
        return [MessageBucketDTO.model_validate(doc) for doc in docs]
