from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ClaimDeliveryInteractor:
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

    async def __call__(self) -> Delivery | None:
        async with self._uow:
            row = await self._delivery_writer.find_next_available(
                at=Timestamp(self._clock.now())
            )
            if row is None:
                return None
            if (
                row.user_id is None
                or row.chat_id != row.user_id
                or (not await self._access_policy.allowed(user_id=row.user_id.value))
            ):
                row.cancel()
                return None
            row.claim(Timestamp(self._clock.now()))
            return row
