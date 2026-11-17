from abc import ABC, abstractmethod

from universal_bot.application.query_model.telegram_update import (
    TelegramUpdateQueryModel,
)
from universal_bot.domain.enum.telegram_update.state import TelegramUpdateState


class ITelegramUpdateReader(ABC):
    @abstractmethod
    async def get_page_by_state(
        self, *, state: TelegramUpdateState, limit: int
    ) -> list[TelegramUpdateQueryModel]: ...
