from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from universal_bot.application.command.access.initialize_service import (
    InitializeServiceInteractor,
)
from universal_bot.composition.configuration.app_configuration import AppConfiguration
from universal_bot.composition.ioc.provider_registry import get_provider
from universal_bot.domain.exception.base import BaseError
from universal_bot.presentation.http.api_router import create_api_router
from universal_bot.presentation.http.exception.handler import (
    invalid,
    problem,
    unexpected,
)
from universal_bot.presentation.http.health.router import (
    create_health_router,
)
from universal_bot.presentation.http.public_api.middleware.metadata import metadata
from universal_bot.presentation.http.telegram.router import (
    create_telegram_router,
)


def create_ioc_container(
    configuration: AppConfiguration, *di_providers: Provider
) -> AsyncContainer:
    return make_async_container(
        *get_provider(),
        *di_providers,
        FastapiProvider(),
        context={AppConfiguration: configuration},
    )


def create_api_app(
    container: AsyncContainer, configuration: AppConfiguration
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            async with container() as scope:
                initialize = await scope.get(InitializeServiceInteractor)
                await initialize()
            yield
        finally:
            await container.close()

    app = FastAPI(
        title=configuration.server.app_name,
        version=configuration.server.api_version,
        lifespan=lifespan,
        docs_url="/docs"
        if (
            configuration.server.env != "production"
            and configuration.server.enable_api_docs
        )
        else None,
        redoc_url=None,
        openapi_url="/openapi.json"
        if (
            configuration.server.env != "production"
            and configuration.server.enable_api_docs
        )
        else None,
    )
    app.middleware("http")(metadata)
    app.add_exception_handler(BaseError, problem)
    app.add_exception_handler(RequestValidationError, invalid)
    app.add_exception_handler(Exception, unexpected)
    app.include_router(create_health_router())
    app.include_router(create_telegram_router())
    app.include_router(create_api_router())
    setup_dishka(container, app)
    return app


def build_api_app(configuration: AppConfiguration | None = None) -> FastAPI:
    configuration = configuration or AppConfiguration.model_validate({})
    return create_api_app(create_ioc_container(configuration), configuration)
