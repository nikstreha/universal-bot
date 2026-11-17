from sqlalchemy import or_, select

from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.delivery import delivery_table
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLADeliveryWriter(IDeliveryWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_next_available(self, *, at: Timestamp) -> Delivery | None:
        at_raw = convert_to_primitive(at)
        statement = select(Delivery).where(
            delivery_table.c.state.in_(("queued", "sending")),
            delivery_table.c.next_attempt_at <= at_raw,
            or_(
                delivery_table.c.state == "queued",
                delivery_table.c.lease_until <= at_raw,
            ),
        )
        statement = statement.order_by(
            delivery_table.c.next_attempt_at,
            delivery_table.c.created_at,
            delivery_table.c.id,
        ).limit(1)
        return (await self._session.scalars(statement)).first()

    async def find_by_id(self, *, key: DeliveryId) -> Delivery | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Delivery, key_raw)

    async def find_by_dedup_key(
        self, *, dedup_key: DeduplicationKey
    ) -> Delivery | None:
        dedup_key_raw = convert_to_primitive(dedup_key)
        statement = select(Delivery)
        statement = statement.where(delivery_table.c.dedup_key == dedup_key_raw)
        return (await self._session.scalars(statement.limit(1))).first()

    async def add(self, *, entity: Delivery) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def cancel_for_user(self, *, user_id: TelegramUserId, at: Timestamp) -> None:
        statement = select(Delivery).where(
            delivery_table.c.user_id == user_id.value,
            delivery_table.c.state.in_(("queued", "sending")),
        )
        for row in await self._session.scalars(statement):
            row.cancel()
