from universal_bot.infrastructure.exeption import InfrastructureError


class OpenAIError(InfrastructureError):
    pass


class OpenAIConnectionError(OpenAIError):
    pass
