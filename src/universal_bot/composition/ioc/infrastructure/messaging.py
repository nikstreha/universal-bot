from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from universal_bot.application.port.messaging.telegram import ITelegramClient
from universal_bot.composition.configuration.telegram_configuration import (
    TelegramConfiguration,
)
from universal_bot.infrastructure.telegram.gateway import TelegramGateway


class MessagingProvider(Provider):
    @provide(scope=Scope.APP)
    async def telegram(
        self, config: TelegramConfiguration
    ) -> AsyncIterator[ITelegramClient]:
        gateway = TelegramGateway(config.token)
        try:
            yield gateway
        finally:
            await gateway.close()
