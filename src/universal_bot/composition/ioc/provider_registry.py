from collections.abc import Iterable

from dishka import Provider

from src.universal_bot.composition.ioc.configuration import ConfigurationProvider
from src.universal_bot.composition.ioc.infrastructure import _infrastructure_provider


def get_provider() -> Iterable[Provider]:
    return [
        ConfigurationProvider(),
        *_infrastructure_provider(),
    ]
