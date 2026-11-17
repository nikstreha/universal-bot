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
            raise TelegramErrorError(
                "Ошибка Telegram",
                telegram_code=payload.get("error_code"),
                retry_after=payload.get("parameters", {}).get("retry_after", 30),
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
