import logging

from universal_bot.application.command.access.apply_rate_limit import (
    ApplyRateLimitInteractor,
)
from universal_bot.application.command.access.observe_telegram_user import (
    ObserveTelegramUserInteractor,
)
from universal_bot.application.command.access.request_access import (
    RequestAccessInteractor,
)
from universal_bot.application.command.auth.bind_login_attempt import (
    BindLoginAttemptInteractor,
)
from universal_bot.application.command.auth.confirm_login_attempt import (
    ConfirmLoginAttemptInteractor,
)
from universal_bot.application.command.telegram.accept_audio import (
    AcceptAudioInteractor,
)
from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.port.messaging.telegram import ITelegramClient
from universal_bot.application.query.telegram.get_access_request_status import (
    GetAccessRequestStatusInteractor,
)
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.presentation.telegram.handler.admin import TelegramAdminHandler
from universal_bot.presentation.telegram.keyboard.admin import ADMIN_KEYBOARD
from universal_bot.presentation.telegram.keyboard.inline import inline


class TelegramUpdateHandler:
    def __init__(
        self,
        *,
        accept_audio: AcceptAudioInteractor,
        apply_rate_limit: ApplyRateLimitInteractor,
        bind_login_attempt: BindLoginAttemptInteractor,
        confirm_login_attempt: ConfirmLoginAttemptInteractor,
        gateway: ITelegramClient,
        get_access_request_status: GetAccessRequestStatusInteractor,
        observe_telegram_user: ObserveTelegramUserInteractor,
        policy: Policy,
        request_access: RequestAccessInteractor,
        admin_handler: TelegramAdminHandler,
    ) -> None:
        self._accept_audio = accept_audio
        self._apply_rate_limit = apply_rate_limit
        self._bind_login_attempt = bind_login_attempt
        self._confirm_login_attempt = confirm_login_attempt
        self._gateway = gateway
        self._get_access_request_status = get_access_request_status
        self._observe_telegram_user = observe_telegram_user
        self._policy = policy
        self._request_access = request_access
        self._admin_handler = admin_handler

    async def handle(self, update: dict) -> None:
        callback = update.get("callback_query")
        message = callback.get("message", {}) if callback else update.get("message", {})
        actor = callback["from"] if callback else message.get("from", {})
        if (
            not actor
            or actor.get("is_bot")
            or message.get("chat", {}).get("type") != "private"
            or (message["chat"]["id"] != actor.get("id"))
        ):
            return
        user_id = actor["id"]
        chat_id = message["chat"]["id"]
        await self._apply_rate_limit(key=f"telegram:{user_id}", maximum=30)
        text = message.get("text", "") if not callback else ""
        data = callback.get("data", "") if callback else ""
        if user_id != self._policy.admin_id and (
            text.split(" ", 1)[0].split("@", 1)[0] == "/admin"
            or text
            in {
                "Добавить пользователя",
                "Пользователи",
                "Получить уведомления",
                "Запросы на доступ",
                "Состояние сервера",
            }
            or data.startswith(
                (
                    "revoke:",
                    "revoke_yes:",
                    "notifications:",
                    "read:",
                    "requests:",
                    "approve:",
                    "reject:",
                    "grant:",
                )
            )
        ):
            logging.getLogger(__name__).warning(
                "Administrative Telegram action denied",
                extra={"event": "admin_access_denied", "actor_id": user_id},
            )
            await self._gateway.message(chat_id, "Недостаточно прав.")
            if callback:
                await self._gateway.answer(callback["id"])
            return
        user, allowed = await self._observe_telegram_user(
            user_id=user_id,
            name=" ".join(
                filter(None, (actor.get("first_name"), actor.get("last_name")))
            ),
        )
        if callback:
            await self._gateway.answer(callback["id"])
        if text.startswith("/start login_"):
            attempt = await self._bind_login_attempt(
                attempt_id=text.split("login_", 1)[1], user_id=user_id
            )
            await self._gateway.message(
                chat_id,
                f"Вход в storage\nУстройство: {attempt.device_name.value}\nКод: {attempt.login_code.value}\n\nСверьте код с приложением и подтвердите вход, если это ваша попытка.",
                inline(
                    (
                        ("Подтвердить вход", "login_yes:" + str(attempt.id_.value)),
                        ("Отказать", "login_no:" + str(attempt.id_.value)),
                    )
                ),
            )
            return
        if data.startswith(("login_yes:", "login_no:")):
            result = await self._confirm_login_attempt(
                attempt_id=data.split(":", 1)[1],
                user_id=user_id,
                accepted=data.startswith("login_yes:"),
            )
            if result is LoginAttemptStatus.DENIED:
                await self._show_access_denied(chat_id=chat_id, user_id=user_id)
            else:
                await self._gateway.message(
                    chat_id,
                    "Вход подтверждён. Вернитесь в storage."
                    if result is LoginAttemptStatus.READY
                    else "Вход отменён.",
                )
            return
        if text.startswith("/start"):
            await self._observe_telegram_user(
                user_id=user_id, event_key=f"bot:{update['update_id']}", source="bot"
            )
        if data == "request_access":
            request, created = await self._request_access(user_id=user_id, source="bot")
            await self._gateway.message(
                chat_id,
                f"{('Запрос отправлен' if created else 'Запрос уже существует')}. Статус: {request.status}",
            )
            return
        if data == "request_status":
            await self._gateway.message(
                chat_id,
                "Статус запроса: "
                + await self._get_access_request_status(user_id=user_id),
            )
            return
        if not allowed:
            await self._show_access_denied(chat_id=chat_id, user_id=user_id)
            return
        if user_id == self._policy.admin_id:
            if await self._admin_handler.handle(
                chat_id=chat_id, actor_id=user_id, text=text, data=data
            ):
                return
        audio = message.get("voice") or message.get("audio") or message.get("document")
        if audio:
            _, created = await self._accept_audio(
                user_id=user_id,
                chat_id=chat_id,
                message_id=message["message_id"],
                file_id=audio["file_id"],
                size=audio.get("file_size"),
            )
            if created:
                await self._gateway.message(
                    chat_id,
                    "Принято в очередь на расшифровку.",
                    reply_to=message["message_id"],
                )
            return
        await self._gateway.message(
            chat_id,
            "Пришлите голосовое сообщение или аудиофайл до 20 МБ. Я верну расшифровку.",
            ADMIN_KEYBOARD if user_id == self._policy.admin_id else None,
        )

    async def _show_access_denied(self, *, chat_id: int, user_id: int) -> None:
        logging.getLogger(__name__).warning(
            "Telegram access denied",
            extra={"event": "access_denied", "actor_id": user_id},
        )
        status = await self._get_access_request_status(user_id=user_id)
        keyboard = (
            inline((("Запросить доступ у админа", "request_access"),))
            if status == "not_requested"
            else inline((("Статус запроса", "request_status"),))
        )
        await self._gateway.message(
            chat_id, f"Доступ пока не открыт. Ваш Telegram ID: {user_id}", keyboard
        )
