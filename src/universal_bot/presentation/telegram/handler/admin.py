import json

from universal_bot.application.command.access.decide_access_request import (
    DecideAccessRequestInteractor,
)
from universal_bot.application.command.access.grant_access import GrantAccessInteractor
from universal_bot.application.command.access.mark_login_notifications_read import (
    MarkLoginNotificationsReadInteractor,
)
from universal_bot.application.command.access.revoke_access import (
    RevokeAccessInteractor,
)
from universal_bot.application.command.telegram.clear_telegram_dialog import (
    ClearTelegramDialogInteractor,
)
from universal_bot.application.command.telegram.telegram_dialog import (
    TelegramDialogInteractor,
)
from universal_bot.application.port.messaging.telegram import ITelegramClient
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.query.access.get_access_request_list import (
    GetAccessRequestListInteractor,
)
from universal_bot.application.query.access.get_login_notification_list import (
    GetLoginNotificationListInteractor,
)
from universal_bot.application.query.access.get_user_list import GetUserListInteractor
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.presentation.telegram.keyboard.admin import ADMIN_KEYBOARD
from universal_bot.presentation.telegram.keyboard.inline import inline


class TelegramAdminHandler:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clear_telegram_dialog: ClearTelegramDialogInteractor,
        decide_access_request: DecideAccessRequestInteractor,
        gateway: ITelegramClient,
        get_access_request_list: GetAccessRequestListInteractor,
        get_login_notification_list: GetLoginNotificationListInteractor,
        get_user_list: GetUserListInteractor,
        grant_access: GrantAccessInteractor,
        mark_login_notifications_read: MarkLoginNotificationsReadInteractor,
        revoke_access: RevokeAccessInteractor,
        secrets: ISecrets,
        storage: IObjectStorage,
        telegram_dialog: TelegramDialogInteractor,
    ) -> None:
        self._access_policy = access_policy
        self._clear_telegram_dialog = clear_telegram_dialog
        self._decide_access_request = decide_access_request
        self._gateway = gateway
        self._get_access_request_list = get_access_request_list
        self._get_login_notification_list = get_login_notification_list
        self._get_user_list = get_user_list
        self._grant_access = grant_access
        self._mark_login_notifications_read = mark_login_notifications_read
        self._revoke_access = revoke_access
        self._secrets = secrets
        self._storage = storage
        self._telegram_dialog = telegram_dialog

    async def handle(
        self, *, chat_id: int, actor_id: int, text: str, data: str
    ) -> bool:
        await self._access_policy.require_admin(actor_id=actor_id)
        if text in ("/admin", "/start"):
            await self._gateway.message(chat_id, "storage · управление", ADMIN_KEYBOARD)
        elif text == "Добавить пользователя":
            await self._telegram_dialog(actor_id=actor_id, action="add_user")
            await self._gateway.message(
                chat_id, "Введите числовой Telegram ID пользователя."
            )
        elif text == "Пользователи":
            users = await self._get_user_list(actor_id=actor_id)
            for user in users:
                keyboard = (
                    inline((("Удалить доступ", f"revoke:{user.id}"),))
                    if user.id != actor_id
                    else None
                )
                await self._gateway.message(
                    chat_id,
                    f"{user.name or 'Пользователь'}\nID: {user.id}\nФайлов: {user.files} · {user.bytes / 1024**2:.1f} МБ",
                    keyboard,
                )
        elif data.startswith("revoke:"):
            target = data.split(":", 1)[1]
            await self._gateway.message(
                chat_id,
                f"Удалить доступ {target}? Все файлы сохранятся.",
                inline(
                    (("Удалить доступ", "revoke_yes:" + target), ("Отмена", "cancel"))
                ),
            )
        elif data.startswith("revoke_yes:"):
            await self._revoke_access(
                actor_id=actor_id, user_id=int(data.split(":", 1)[1])
            )
            await self._gateway.message(chat_id, "Доступ удалён, файлы сохранены.")
        elif text == "Получить уведомления" or data.startswith("notifications:"):
            offset = int(data.split(":")[1]) if data else 0
            rows = await self._get_login_notification_list(
                actor_id=actor_id, offset=offset
            )
            if not rows:
                await self._gateway.message(chat_id, "Новых уведомлений нет.")
            else:
                nonce = self._secrets.identity()
                await self._telegram_dialog(
                    actor_id=actor_id,
                    action="read_notifications",
                    payload={"nonce": nonce, "ids": [r.id for r, _ in rows]},
                )
                body = "\n\n".join(
                    (
                        f"{user.name} · {row.user_id}\n{row.source} · {row.outcome}"
                        for row, user in rows
                    )
                )
                buttons = [(("Отметить прочитанными", "read:" + nonce),)]
                if len(rows) == 10:
                    buttons.append((("Следующие", f"notifications:{offset + 10}"),))
                await self._gateway.message(chat_id, body, inline(*buttons))
        elif data.startswith("read:"):
            dialog = await self._telegram_dialog(actor_id=actor_id)
            if (
                dialog
                and dialog.action == "read_notifications"
                and (json.loads(dialog.payload)["nonce"] == data.split(":", 1)[1])
            ):
                await self._mark_login_notifications_read(
                    actor_id=actor_id, ids=json.loads(dialog.payload)["ids"]
                )
                await self._clear_telegram_dialog(actor_id=actor_id)
                await self._gateway.message(
                    chat_id, "Показанные уведомления прочитаны."
                )
            else:
                await self._gateway.message(
                    chat_id, "Страница устарела. Получите уведомления ещё раз."
                )
        elif text == "Запросы на доступ" or data.startswith("requests:"):
            offset = int(data.split(":")[1]) if data else 0
            rows = await self._get_access_request_list(actor_id=actor_id, offset=offset)
            if not rows:
                await self._gateway.message(chat_id, "Нет ожидающих запросов.")
            for row, user in rows:
                await self._gateway.message(
                    chat_id,
                    f"{user.name or 'Пользователь'} · {row.user_id}\nИсточник: {row.source}",
                    inline(
                        (
                            ("Одобрить", "approve:" + row.id),
                            ("Отклонить", "reject:" + row.id),
                        )
                    ),
                )
            if len(rows) == 10:
                await self._gateway.message(
                    chat_id,
                    "Ещё запросы",
                    inline((("Следующие", f"requests:{offset + 10}"),)),
                )
        elif data.startswith(("approve:", "reject:")):
            await self._decide_access_request(
                actor_id=actor_id,
                request_id=data.split(":", 1)[1],
                approved=data.startswith("approve:"),
            )
            await self._gateway.message(chat_id, "Решение сохранено.")
        elif text == "Состояние сервера":
            try:
                await self._storage.ready()
                status = "доступно"
            except Exception:
                status = "недоступно"
            await self._gateway.message(chat_id, "Хранилище: " + status)
        elif data == "cancel":
            await self._clear_telegram_dialog(actor_id=actor_id)
            await self._gateway.message(chat_id, "Отменено.")
        else:
            dialog = await self._telegram_dialog(actor_id=actor_id)
            if dialog and dialog.action == "add_user" and text:
                if not text.isdecimal():
                    await self._gateway.message(chat_id, "Нужен числовой Telegram ID.")
                else:
                    target = int(text)
                    await self._gateway.message(
                        chat_id,
                        f"Открыть доступ пользователю {target}?",
                        inline((("Добавить", f"grant:{target}"), ("Отмена", "cancel"))),
                    )
                return True
            if data.startswith("grant:"):
                await self._grant_access(
                    actor_id=actor_id, user_id=int(data.split(":", 1)[1])
                )
                await self._clear_telegram_dialog(actor_id=actor_id)
                await self._gateway.message(chat_id, "Доступ открыт.")
            else:
                return False
        return True
