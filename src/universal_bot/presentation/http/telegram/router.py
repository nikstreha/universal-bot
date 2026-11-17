import json
from hmac import compare_digest

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Request, Response

from universal_bot.application.command.telegram.receive_telegram_updates import (
    ReceiveTelegramUpdatesInteractor,
)
from universal_bot.presentation.http.telegram.configuration import WebhookConfiguration


def create_telegram_router() -> APIRouter:
    router = APIRouter()

    @router.post("/telegram/webhook", include_in_schema=False)
    @inject
    async def webhook(
        request: Request,
        *,
        configuration: FromDishka[WebhookConfiguration],
        receive: FromDishka[ReceiveTelegramUpdatesInteractor],
    ) -> Response:
        if not configuration.enabled:
            return Response(status_code=404)
        supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not configuration.secret or not compare_digest(
            supplied.encode("utf-8"), configuration.secret.encode("ascii")
        ):
            return Response(status_code=403)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > configuration.max_body_bytes:
                return Response(status_code=413)
            body.extend(chunk)
        try:
            update = json.loads(body)
        except ValueError, UnicodeDecodeError:
            return Response(status_code=400)
        if (
            not isinstance(update, dict)
            or type(update.get("update_id")) is not int
            or not 0 <= update["update_id"] < 2**63
        ):
            return Response(status_code=400)
        # Acknowledge only after the inbox transaction commits; Telegram retries failures.
        await receive(updates=[update])
        return Response(status_code=200)

    return router
