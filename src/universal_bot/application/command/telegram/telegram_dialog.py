import json

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_dialog.writer import (
    IAccessDialogWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.entity.access_dialog import AccessDialog
from universal_bot.domain.enum.admin_dialog.action import AdminDialogAction
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class TelegramDialogInteractor:
    def __init__(
        self,
        *,
        access_dialog_writer: IAccessDialogWriter,
        access_policy: AccessPolicy,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._access_dialog_writer = access_dialog_writer
        self._access_policy = access_policy
        self._clock = clock
        self._uow = uow

    async def __call__(
        self, *, actor_id: int, action: str | None = None, payload: dict | None = None
    ) -> AccessDialog | None:
        await self._access_policy.require_admin(actor_id=actor_id)
        async with self._uow:
            row = await self._access_dialog_writer.find_by_id(
                key=TelegramUserId(actor_id)
            )
            if action:
                if row:
                    row.update(
                        AdminDialogAction(action),
                        json.dumps(payload or {}),
                        Timestamp(self._clock.now()),
                    )
                else:
                    row = AccessDialog(
                        admin_id=TelegramUserId(actor_id),
                        action=AdminDialogAction(action),
                        payload=json.dumps(payload or {}),
                        expires_at=Timestamp(self._clock.now() + 900),
                    )
                    await self._access_dialog_writer.add(entity=row)
            return (
                row
                if row and not row.is_expired(Timestamp(self._clock.now()))
                else None
            )
