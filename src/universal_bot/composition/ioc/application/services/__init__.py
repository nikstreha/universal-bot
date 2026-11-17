from dishka import Provider

from universal_bot.composition.ioc.application.services.access import (
    AccessServicesProvider,
)


def _services_provider() -> tuple[Provider, ...]:
    return (AccessServicesProvider(),)
