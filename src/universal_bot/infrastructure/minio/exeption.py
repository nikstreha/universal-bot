from universal_bot.infrastructure.exeption import InfrastructureError, NotConnectedError


class MinioNotConnectedError(NotConnectedError):
    pass


class MinioError(InfrastructureError):
    pass


class MinioStorageError(MinioError):
    pass


class MinioClientError(MinioError):
    pass
