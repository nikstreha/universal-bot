class InfrastructureError(Exception):
    pass


class NotConnectedError(InfrastructureError):
    pass


class InfrastructureTimeoutError(InfrastructureError):
    pass
