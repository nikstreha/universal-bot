from datetime import UTC, datetime
from typing import Self

from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.message.message import Message
from universal_bot.domain.value_object.message_bucket.count import BucketMessageCount
from universal_bot.domain.value_object.message_bucket.id import MessageBucketId
from universal_bot.domain.value_object.message_bucket.seq import BucketSeq


class MessageBucket(Entity[MessageBucketId]):
    def __init__(
        self,
        *,
        id_: MessageBucketId,
        chat_id: ChatId,
        seq: BucketSeq,
        messages: list[Message],
        count: BucketMessageCount,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id_=id_)
        self.chat_id = chat_id
        self.seq = seq
        self.messages = messages
        self.count = count
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create(
        cls,
        chat_id: ChatId,
        seq: BucketSeq,
        message: Message,
    ) -> Self:
        now = datetime.now(UTC)
        bucket_id = MessageBucketId(f"{chat_id.value}:{seq.value}")
        return cls(
            id_=bucket_id,
            chat_id=chat_id,
            seq=seq,
            messages=[message],
            count=BucketMessageCount(1),
            created_at=now,
            updated_at=now,
        )

    def is_full(self, bucket_size: int) -> bool:
        return self.count.value >= bucket_size
