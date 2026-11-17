from dishka import Provider

from universal_bot.composition.ioc.application.command import _command_provider
from universal_bot.composition.ioc.application.query import _query_provider
from universal_bot.composition.ioc.application.services import _services_provider


def _application_provider() -> tuple[Provider, ...]:
    return (*_command_provider(), *_query_provider(), *_services_provider())
