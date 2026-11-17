import json

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.service_state.writer import (
    IServiceStateWriter,
)
from universal_bot.application.port.persistence.repository.telegram_update.writer import (
    ITelegramUpdateWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.entity.service_state import ServiceState
from universal_bot.domain.entity.telegram_update import TelegramUpdate
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId
from universal_bot.domain.value_object.service_state.key import ServiceStateKey
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ReceiveTelegramUpdatesInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        service_state_writer: IServiceStateWriter,
        telegram_update_writer: ITelegramUpdateWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._clock = clock
        self._service_state_writer = service_state_writer
        self._telegram_update_writer = telegram_update_writer
        self._uow = uow

    async def __call__(
        self, *, updates: list[dict], advance_offset: bool = False
    ) -> None:
        async with self._uow:
            for update in updates:
                if not await self._telegram_update_writer.find_by_id(
                    key=TelegramUpdateId(update["update_id"])
                ):
                    await self._telegram_update_writer.add(
                        entity=TelegramUpdate(
                            id_=TelegramUpdateId(update["update_id"]),
                            payload=json.dumps(update, ensure_ascii=False),
                            created_at=Timestamp(self._clock.now()),
                        )
                    )
            if advance_offset and updates:
                key = ServiceStateKey("telegram_offset")
                state = await self._service_state_writer.find_by_id(key=key)
                value = str(max(update["update_id"] for update in updates) + 1)
                if state is None:
                    await self._service_state_writer.add(
                        entity=ServiceState(key=key, value=value)
                    )
                else:
                    state.value = value
