from dataclasses import dataclass

from dishka import AsyncContainer, Provider

from universal_bot.application.command.access.initialize_service import (
    InitializeServiceInteractor,
)
from universal_bot.application.port.messaging.telegram import ITelegramClient
from universal_bot.composition.configuration.app_configuration import AppConfiguration
from universal_bot.composition.configuration.telegram_configuration import (
    TelegramConfiguration,
)
from universal_bot.composition.worker_app import create_ioc_container
from universal_bot.presentation.worker.messaging.telegram_worker import TelegramWorker


@dataclass(frozen=True, slots=True)
class TelegramApp:
    container: AsyncContainer
    worker: TelegramWorker

    async def up(self) -> None:
        try:
            async with self.container() as scope:
                await (await scope.get(InitializeServiceInteractor))()
            configuration = await self.container.get(TelegramConfiguration)
            gateway = await self.container.get(ITelegramClient)
            if configuration.mode == "webhook":
                await gateway.set_webhook(
                    url=configuration.webhook_url, secret=configuration.webhook_secret
                )
            else:
                await gateway.delete_webhook()
            await self.worker.run(polling=configuration.mode == "polling")
        finally:
            await self.container.close()


async def create_telegram_app(
    configuration: AppConfiguration | None = None, *di_providers: Provider
) -> TelegramApp:
    configuration = configuration or AppConfiguration.model_validate({})
    container = create_ioc_container(configuration, *di_providers)
    return TelegramApp(container=container, worker=TelegramWorker(container))
