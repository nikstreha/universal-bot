from dishka import Provider, Scope, from_context, provide

from src.universal_bot.composition.configuration.config import Settings


class ConfigurationProvider(Provider):
    scope = Scope.APP

    configuration = from_context(provides=Settings)

    @provide
    def get_settings(self, configuration: Settings) -> Settings:
        return configuration
