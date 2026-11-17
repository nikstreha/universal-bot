from dataclasses import dataclass

from dishka import AsyncContainer, Provider, make_async_container

from universal_bot.application.command.access.initialize_service import (
    InitializeServiceInteractor,
)
from universal_bot.composition.configuration.app_configuration import AppConfiguration
from universal_bot.composition.ioc.provider_registry import get_provider
from universal_bot.presentation.worker.job_worker import JobWorker


def create_ioc_container(
    configuration: AppConfiguration, *di_providers: Provider
) -> AsyncContainer:
    return make_async_container(
        *get_provider(), *di_providers, context={AppConfiguration: configuration}
    )


@dataclass(frozen=True, slots=True)
class WorkerApp:
    container: AsyncContainer
    worker: JobWorker

    async def up(self) -> None:
        try:
            async with self.container() as scope:
                await (await scope.get(InitializeServiceInteractor))()
            await self.worker.run()
        finally:
            await self.container.close()


async def create_worker_app(
    configuration: AppConfiguration | None = None, *di_providers: Provider
) -> WorkerApp:
    configuration = configuration or AppConfiguration.model_validate({})
    container = create_ioc_container(configuration, *di_providers)
    return WorkerApp(container=container, worker=JobWorker(container))
