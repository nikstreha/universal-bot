from dishka import Provider

from universal_bot.composition.ioc.application import _application_provider
from universal_bot.composition.ioc.configuration import ConfigurationProvider
from universal_bot.composition.ioc.infrastructure import _infrastructure_provider
from universal_bot.composition.ioc.presentation import PresentationProvider


def get_provider() -> tuple[Provider, ...]:
    return (
        ConfigurationProvider(),
        *_infrastructure_provider(),
        *_application_provider(),
        PresentationProvider(),
    )
