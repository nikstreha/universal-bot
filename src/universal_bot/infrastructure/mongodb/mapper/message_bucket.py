from universal_bot.domain.entity.message_bucket import MessageBucket
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.message.content import MessageContent
from universal_bot.domain.value_object.message.id import MessageId
from universal_bot.domain.value_object.message.message import Message
from universal_bot.domain.value_object.message.token_used import TokenUsed
from universal_bot.domain.value_object.message_bucket.count import BucketMessageCount
from universal_bot.domain.value_object.message_bucket.id import MessageBucketId
from universal_bot.domain.value_object.message_bucket.seq import BucketSeq
from universal_bot.infrastructure.mongodb.documents.message_bucket import (
    MessageBucketDocument,
)
from universal_bot.infrastructure.mongodb.mapper.message import MessageMapper


class MessageBucketMapper:
    @staticmethod
    def to_document(bucket: MessageBucket) -> MessageBucketDocument:
        return MessageBucketDocument(
            _id=bucket.id_.value,
            chat_id=bucket.chat_id.value,
            seq=bucket.seq.value,
            messages=[MessageMapper.to_document(msg) for msg in bucket.messages],
            count=bucket.count.value,
            created_at=bucket.created_at,
            updated_at=bucket.updated_at,
        )

    @staticmethod
    def to_entity(doc: MessageBucketDocument) -> MessageBucket:
        messages = [
            Message(
                id_=MessageId(msg.id_),
                role=msg.role,
                content=MessageContent(msg.content),
                created_at=msg.created_at,
                reply_from=MessageId(msg.reply_from) if msg.reply_from else None,
                token_used=TokenUsed(msg.token_used) if msg.token_used else None,
            )
            for msg in doc.messages
        ]
        return MessageBucket(
            id_=MessageBucketId(doc.id_),
            chat_id=ChatId(doc.chat_id),
            seq=BucketSeq(doc.seq),
            messages=messages,
            count=BucketMessageCount(doc.count),
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
