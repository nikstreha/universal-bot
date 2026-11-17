from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.telegram_update.state import TelegramUpdateState
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class TelegramUpdate(Entity[TelegramUpdateId]):
    _id: TelegramUpdateId
    payload: str
    created_at: Timestamp
    state: TelegramUpdateState

    def __init__(
        self,
        *,
        id_: TelegramUpdateId,
        payload: str,
        created_at: Timestamp,
        state: TelegramUpdateState = TelegramUpdateState.QUEUED,
    ) -> None:
        super().__init__(id_=id_)
        self.payload = payload
        self.created_at = created_at
        self._state = state

    @property
    def state(self) -> TelegramUpdateState:
        return self._state

    def mark_processed(self) -> None:
        self._state = TelegramUpdateState.COMPLETED
