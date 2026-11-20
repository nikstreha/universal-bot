import asyncio
import json
import logging

from dishka import AsyncContainer

from universal_bot.application.command.telegram.authorize_delivery import (
    AuthorizeDeliveryInteractor,
)
from universal_bot.application.command.telegram.claim_delivery import (
    ClaimDeliveryInteractor,
)
from universal_bot.application.command.telegram.complete_delivery import (
    CompleteDeliveryInteractor,
)
from universal_bot.application.command.telegram.complete_telegram_update import (
    CompleteTelegramUpdateInteractor,
)
from universal_bot.application.command.telegram.receive_telegram_updates import (
    ReceiveTelegramUpdatesInteractor,
)
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.messaging.telegram import ITelegramClient
from universal_bot.application.query.telegram.get_pending_telegram_updates import (
    GetPendingTelegramUpdatesInteractor,
)
from universal_bot.application.query.telegram.get_telegram_offset import (
    GetTelegramOffsetInteractor,
)
from universal_bot.domain.exception.base import BaseError
from universal_bot.presentation.telegram.handler.update import TelegramUpdateHandler

logger = logging.getLogger(__name__)


class TelegramWorker:
    def __init__(self, container: AsyncContainer) -> None:
        self._container = container

    async def _poll(self, gateway: ITelegramClient) -> None:
        while True:
            try:
                async with self._container() as scope:
                    get_offset = await scope.get(GetTelegramOffsetInteractor)
                    offset = await get_offset()
                updates = await gateway.get_updates(offset=offset)
                if updates:
                    async with self._container() as scope:
                        receive = await scope.get(ReceiveTelegramUpdatesInteractor)
                        await receive(updates=updates, advance_offset=True)
            except Exception as exc:
                logger.warning(
                    "Telegram polling deferred: %s",
                    type(exc).__name__,
                    exc_info=exc,
                    extra={"event": "telegram_polling_failed"},
                )
                delay = 5
                if isinstance(exc, BaseError) and exc.payload.get("telegram_code") == 429:
                    retry_after = exc.payload.get("retry_after")
                    if type(retry_after) is int and 0 <= retry_after <= 3600:
                        delay = max(delay, retry_after)
                await asyncio.sleep(delay)

    async def _process(self, gateway: ITelegramClient) -> None:
        while True:
            try:
                async with self._container() as scope:
                    pending = await scope.get(GetPendingTelegramUpdatesInteractor)
                    rows = await pending()
                for row in rows:
                    async with self._container() as scope:
                        handler = await scope.get(TelegramUpdateHandler)
                        processed = await scope.get(CompleteTelegramUpdateInteractor)
                        try:
                            await handler.handle(json.loads(row.payload))
                        except BaseError as exc:
                            update = json.loads(row.payload)
                            message = update.get("message") or update.get(
                                "callback_query", {}
                            ).get("message", {})
                            if message.get("chat", {}).get("type") == "private":
                                await gateway.message(
                                    message["chat"]["id"], exc.message
                                )
                        await processed(update_id=row.id)
                await asyncio.sleep(0.5)
            except Exception as exc:
                logger.warning(
                    "Telegram update deferred: %s",
                    type(exc).__name__,
                    exc_info=exc,
                    extra={"event": "telegram_update_failed"},
                )
                await asyncio.sleep(3)

    async def _deliver(self, gateway: ITelegramClient, clock: IClock) -> None:
        while True:
            try:
                async with self._container() as scope:
                    claim = await scope.get(ClaimDeliveryInteractor)
                    row = await claim()
                if not row:
                    await asyncio.sleep(1)
                    continue
                if row.lease_until is None:
                    raise RuntimeError("Claimed delivery has no lease")
                async with self._container() as scope:
                    authorize = await scope.get(AuthorizeDeliveryInteractor)
                    row = await authorize(
                        delivery_id=str(row.id_.value),
                        lease_until=row.lease_until.value,
                    )
                    if row is None:
                        continue
                    complete = await scope.get(CompleteDeliveryInteractor)
                    try:
                        if row.edit_message_id is not None:
                            if row.filename:
                                result = await gateway.edit_document(
                                    row.chat_id,
                                    row.edit_message_id,
                                    row.text,
                                    row.filename,
                                )
                            else:
                                result = await gateway.edit_message(
                                    row.chat_id, row.edit_message_id, row.text
                                )
                        elif row.filename:
                            result = await gateway.document(
                                row.chat_id,
                                row.text,
                                row.filename,
                                row.reply_to,
                            )
                        else:
                            result = await gateway.message(
                                row.chat_id,
                                row.text,
                                reply_to=row.reply_to,
                            )
                        await complete(
                            delivery_id=row.id,
                            lease_until=row.lease_until,
                            message_id=result.message_id,
                        )
                    except BaseError as exc:
                        terminal = (
                            exc.details.get("telegram_code") == 403
                            or exc.details.get("telegram_reason")
                            == "message_unavailable"
                            or clock.now() - row.created_at > 86400
                        )
                        await complete(
                            delivery_id=row.id,
                            lease_until=row.lease_until,
                            retry_after=None
                            if terminal
                            else exc.details.get("retry_after", 30),
                            terminal=terminal,
                        )
                    except Exception as exc:
                        logger.warning(
                            "Telegram delivery deferred: %s",
                            type(exc).__name__,
                            exc_info=exc,
                            extra={"event": "telegram_delivery_failed"},
                        )
                        await complete(
                            delivery_id=row.id,
                            lease_until=row.lease_until,
                            retry_after=30,
                        )
            except Exception as exc:
                logger.warning(
                    "Telegram delivery deferred: %s",
                    type(exc).__name__,
                    exc_info=exc,
                    extra={"event": "telegram_delivery_failed"},
                )
                await asyncio.sleep(3)

    async def run(self, *, polling: bool = False) -> None:
        gateway = await self._container.get(ITelegramClient)
        clock = await self._container.get(IClock)
        async with asyncio.TaskGroup() as tasks:
            if polling:
                tasks.create_task(self._poll(gateway))
            tasks.create_task(self._process(gateway))
            tasks.create_task(self._deliver(gateway, clock))
