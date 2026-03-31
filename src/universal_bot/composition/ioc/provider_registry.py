from collections.abc import Iterable

from dishka import Provider

from universal_bot.composition.ioc.application import _application_provider
from universal_bot.composition.ioc.configuration import ConfigurationProvider
from universal_bot.composition.ioc.infrastructure import _infrastructure_provider


def get_provider() -> Iterable[Provider]:
    return [
        ConfigurationProvider(),
        *_infrastructure_provider(),
        *_application_provider(),
    ]
