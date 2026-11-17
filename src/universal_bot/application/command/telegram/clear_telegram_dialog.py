from universal_bot.application.port.persistence.repository.access_dialog.writer import (
    IAccessDialogWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.user.id import TelegramUserId


class ClearTelegramDialogInteractor:
    def __init__(
        self,
        *,
        access_dialog_writer: IAccessDialogWriter,
        access_policy: AccessPolicy,
        uow: IUnitOfWork,
    ) -> None:
        self._access_dialog_writer = access_dialog_writer
        self._access_policy = access_policy
        self._uow = uow

    async def __call__(self, *, actor_id: int) -> None:
        await self._access_policy.require_admin(actor_id=actor_id)
        async with self._uow:
            row = await self._access_dialog_writer.find_by_id(
                key=TelegramUserId(actor_id)
            )
            if row:
                await self._access_dialog_writer.delete(entity=row)
