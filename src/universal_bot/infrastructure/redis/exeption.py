from universal_bot.infrastructure.exeption import InfrastructureError


class RedisError(InfrastructureError):
    pass


class RedisConnectionError(RedisError):
    pass