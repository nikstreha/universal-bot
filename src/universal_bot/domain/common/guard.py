from universal_bot.domain.exception.base import BaseError


def ensure(
    condition: object,
    error: type[BaseError],
    message: str | None = None,
    **payload: object,
) -> None:
    if not condition:
        raise error(message, **payload)
