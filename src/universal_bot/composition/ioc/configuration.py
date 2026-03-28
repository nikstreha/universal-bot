from dishka import Provider, Scope, from_context

from universal_bot.composition.configuration.config import Settings


class ConfigurationProvider(Provider):
    scope = Scope.APP

    configuration = from_context(provides=Settings)
