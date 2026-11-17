from sqlalchemy.orm import composite

from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.enum.delivery.state import DeliveryState
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.delivery import delivery_table
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_delivery_table() -> None:
    delivery_table.c.state.type = EnumStringType(DeliveryState)
    mapping_registry.map_imperatively(
        Delivery,
        delivery_table,
        properties={
            "_id": composite(DeliveryId, delivery_table.c.id),
            "dedup_key": composite(DeduplicationKey, delivery_table.c.dedup_key),
            "chat_id": composite(TelegramUserId, delivery_table.c.chat_id),
            "text": composite(MessageText, delivery_table.c.text),
            "next_attempt_at": composite(Timestamp, delivery_table.c.next_attempt_at),
            "created_at": composite(Timestamp, delivery_table.c.created_at),
            "reply_to": composite(
                TelegramMessageId.from_raw, delivery_table.c.reply_to
            ),
            "filename": delivery_table.c.filename,
            "user_id": composite(TelegramUserId.from_raw, delivery_table.c.user_id),
            "_state": delivery_table.c.state,
            "lease_until": composite(Timestamp.from_raw, delivery_table.c.lease_until),
            "message_id": composite(
                TelegramMessageId.from_raw, delivery_table.c.message_id
            ),
        },
        column_prefix="_raw_",
    )
