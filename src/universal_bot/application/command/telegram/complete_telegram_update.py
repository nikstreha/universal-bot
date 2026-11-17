from universal_bot.application.port.persistence.repository.telegram_update.writer import (
    ITelegramUpdateWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId


class CompleteTelegramUpdateInteractor:
    def __init__(
        self, *, telegram_update_writer: ITelegramUpdateWriter, uow: IUnitOfWork
    ) -> None:
        self._telegram_update_writer = telegram_update_writer
        self._uow = uow

    async def __call__(self, *, update_id: int) -> None:
        async with self._uow:
            row = await self._telegram_update_writer.find_by_id(
                key=TelegramUpdateId(update_id)
            )
            row.mark_processed()
