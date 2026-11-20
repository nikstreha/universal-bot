import json
from typing import Any

import httpx

from universal_bot.application.dto.telegram.message import TelegramMessageDTO
from universal_bot.application.exception.infrastructure.telegram import (
    TelegramErrorError,
)
from universal_bot.application.port.messaging.telegram import ITelegramClient


class TelegramGateway(ITelegramClient):
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("APP__TELEGRAM__TOKEN is required")
        self.client = httpx.AsyncClient(
            base_url=f"https://api.telegram.org/bot{token}/", timeout=60
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _call(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> Any:
        response = await self.client.post(
            method,
            data=data if files else None,
            json=data if not files else None,
            files=files,
        )
        payload = response.json()
        if not payload.get("ok"):
            description = payload.get("description", "").lower()
            if (
                method.startswith("editMessage")
                and payload.get("error_code") == 400
                and "message is not modified" in description
            ):
                return {"message_id": data["message_id"]}
            reason = (
                "message_unavailable"
                if any(
                    value in description
                    for value in (
                        "message to edit not found",
                        "message can't be edited",
                    )
                )
                else None
            )
            if reason is None:
                code = payload.get("error_code")
                if code == 409:
                    reason = (
                        "webhook_active" if "webhook" in description else "polling_conflict"
                    )
                elif code == 429:
                    reason = "rate_limited"
                elif code == 401:
                    reason = "authentication_failed"
                elif type(code) is int and 500 <= code <= 599:
                    reason = "telegram_unavailable"
            raise TelegramErrorError(
                "Ошибка Telegram",
                telegram_code=payload.get("error_code"),
                retry_after=payload.get("parameters", {}).get("retry_after", 30),
                telegram_reason=reason,
            )
        return payload["result"]

    async def set_webhook(self, *, url: str, secret: str) -> None:
        await self._call(
            "setWebhook",
            {
                "url": url,
                "secret_token": secret,
                "allowed_updates": ["message", "callback_query"],
                "max_connections": 4,
                "drop_pending_updates": False,
            },
        )

    async def delete_webhook(self) -> None:
        await self._call("deleteWebhook", {"drop_pending_updates": False})

    async def get_updates(self, *, offset: int, timeout: int = 30) -> list[dict]:
        return await self._call(
            "getUpdates",
            {
                "offset": offset,
                "timeout": timeout,
                "limit": 100,
                "allowed_updates": ["message", "callback_query"],
            },
        )

    async def message(
        self,
        chat_id: int,
        text: str,
        keyboard: dict | None = None,
        reply_to: int | None = None,
    ) -> TelegramMessageDTO:
        body = {"chat_id": chat_id, "text": text}
        if keyboard:
            body["reply_markup"] = keyboard
        if reply_to:
            body["reply_parameters"] = {
                "message_id": reply_to,
                "allow_sending_without_reply": True,
            }
        result = await self._call("sendMessage", body)
        return TelegramMessageDTO(message_id=result["message_id"])

    async def document(
        self, chat_id: int, text: str, filename: str, reply_to: int | None = None
    ) -> TelegramMessageDTO:
        body = {"chat_id": str(chat_id)}
        if reply_to:
            body["reply_parameters"] = json.dumps(
                {"message_id": reply_to, "allow_sending_without_reply": True}
            )
        result = await self._call(
            "sendDocument",
            body,
            {"document": (filename, text.encode(), "text/plain; charset=utf-8")},
        )

        return TelegramMessageDTO(message_id=result["message_id"])

    async def answer(self, callback_id: str, text: str = "") -> None:
        await self._call(
            "answerCallbackQuery", {"callback_query_id": callback_id, "text": text}
        )

    async def edit_message(
        self, chat_id: int, message_id: int, text: str
    ) -> TelegramMessageDTO:
        result = await self._call(
            "editMessageText",
            {"chat_id": chat_id, "message_id": message_id, "text": text},
        )
        return TelegramMessageDTO(message_id=result["message_id"])

    async def edit_document(
        self, chat_id: int, message_id: int, text: str, filename: str
    ) -> TelegramMessageDTO:
        result = await self._call(
            "editMessageMedia",
            {
                "chat_id": str(chat_id),
                "message_id": str(message_id),
                "media": json.dumps(
                    {
                        "type": "document",
                        "media": "attach://document",
                        "caption": "Готово. Расшифровка в файле.",
                    }
                ),
            },
            {"document": (filename, text.encode(), "text/plain; charset=utf-8")},
        )
        return TelegramMessageDTO(message_id=int(result["message_id"]))
