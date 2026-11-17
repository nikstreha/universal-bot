from universal_bot.application.port.persistence.repository.service_state.reader import (
    IServiceStateReader,
)
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidStateError
from universal_bot.domain.value_object.service_state.key import ServiceStateKey


class GetTelegramOffsetInteractor:
    def __init__(self, *, service_state_reader: IServiceStateReader) -> None:
        self._service_state_reader = service_state_reader

    async def __call__(self) -> int:
        row = await self._service_state_reader.find_by_id(
            key=ServiceStateKey("telegram_offset")
        )
        offset = int(row.value) if row is not None else 0
        ensure(offset >= 0, InvalidStateError, "Повреждён Telegram offset")
        return offset
