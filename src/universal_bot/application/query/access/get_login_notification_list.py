from universal_bot.application.port.persistence.repository.admin_notification.reader import (
    IAdminNotificationReader,
)
from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.query_model.admin_notification import (
    AdminNotificationQueryModel,
)
from universal_bot.application.query_model.user import UserQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetLoginNotificationListInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        notification_reader: IAdminNotificationReader,
        user_reader: IUserReader,
    ) -> None:
        self._access_policy = access_policy
        self._notification_reader = notification_reader
        self._user_reader = user_reader

    async def __call__(
        self, *, actor_id: int, unread: bool = True, offset: int = 0
    ) -> list[tuple[AdminNotificationQueryModel, UserQueryModel]]:
        await self._access_policy.require_admin(actor_id=actor_id)
        rows = await self._notification_reader.get_page(
            unread=unread, offset=offset, limit=10
        )
        return [
            (row, await self._user_reader.find_by_id(key=TelegramUserId(row.user_id)))
            for row in rows
        ]
