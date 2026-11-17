from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.admin_notification.writer import (
    IAdminNotificationWriter,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.entity.admin_notification import AdminNotification
from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.notification.outcome import LoginOutcome
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName


class ObserveTelegramUserInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        admin_notification_writer: IAdminNotificationWriter,
        clock: IClock,
        secrets: ISecrets,
        uow: IUnitOfWork,
        user_writer: IUserWriter,
    ) -> None:
        self._access_policy = access_policy
        self._admin_notification_writer = admin_notification_writer
        self._clock = clock
        self._secrets = secrets
        self._uow = uow
        self._user_writer = user_writer

    async def __call__(
        self,
        *,
        user_id: int,
        name: str = "",
        event_key: str | None = None,
        source: str = "bot",
    ) -> tuple[User, bool]:
        async with self._uow:
            user = await self._user_writer.find_by_id(key=TelegramUserId(user_id))
            user_at = Timestamp(self._clock.now())
            if user is None:
                user = User(
                    id_=TelegramUserId(user_id),
                    name=UserName(name[:200]),
                    created_at=user_at,
                    last_seen_at=user_at,
                )
                await self._user_writer.add(entity=user)
            else:
                user.touch(UserName(name[:200]), user_at)
            allowed = await self._access_policy.allowed(user_id=user_id)
            if event_key and (
                not await self._admin_notification_writer.find_by_event_key(
                    event_key=EventKey(event_key)
                )
            ):
                await self._admin_notification_writer.add(
                    entity=AdminNotification(
                        id_=NotificationId(self._secrets.identity()),
                        event_key=EventKey(event_key),
                        user_id=TelegramUserId(user_id),
                        source=AccessSource(source),
                        outcome=LoginOutcome("allowed" if allowed else "denied"),
                        created_at=Timestamp(self._clock.now()),
                    )
                )
            return (user, allowed)
