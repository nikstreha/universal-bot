from universal_bot.application.port.persistence.repository.telegram_update.reader import (
    ITelegramUpdateReader,
)
from universal_bot.application.query_model.telegram_update import (
    TelegramUpdateQueryModel,
)
from universal_bot.domain.enum.telegram_update.state import TelegramUpdateState


class GetPendingTelegramUpdatesInteractor:
    def __init__(self, *, telegram_update_reader: ITelegramUpdateReader) -> None:
        self._telegram_update_reader = telegram_update_reader

    async def __call__(self) -> list[TelegramUpdateQueryModel]:
        return await self._telegram_update_reader.get_page_by_state(
            state=TelegramUpdateState.QUEUED, limit=20
        )
