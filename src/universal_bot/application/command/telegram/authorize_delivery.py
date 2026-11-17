from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class AuthorizeDeliveryInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        delivery_writer: IDeliveryWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._delivery_writer = delivery_writer
        self._uow = uow

    async def __call__(self, *, delivery_id: str, lease_until: int) -> Delivery | None:
        async with self._uow:
            row = await self._delivery_writer.find_by_id(key=DeliveryId(delivery_id))
            if row is None or not row.can_send(
                Timestamp(lease_until), Timestamp(self._clock.now())
            ):
                return None
            if (
                row.user_id is None
                or row.chat_id != row.user_id
                or (not await self._access_policy.allowed(user_id=row.user_id.value))
            ):
                row.cancel()
                return None
            return row
