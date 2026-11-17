from abc import ABC, abstractmethod

from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class IDeliveryWriter(ABC):
    @abstractmethod
    async def find_next_available(self, *, at: Timestamp) -> Delivery | None: ...

    @abstractmethod
    async def find_by_id(self, *, key: DeliveryId) -> Delivery | None: ...

    @abstractmethod
    async def find_by_dedup_key(
        self, *, dedup_key: DeduplicationKey
    ) -> Delivery | None: ...

    @abstractmethod
    async def add(self, *, entity: Delivery) -> None: ...

    @abstractmethod
    async def cancel_for_user(
        self, *, user_id: TelegramUserId, at: Timestamp
    ) -> None: ...
