from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidRequestError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class IdempotencyKey(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (
            bool(self.value)
            and len(self.value) <= 120
            and not any(ord(c) < 32 for c in self.value)
        ):
            raise InvalidRequestError("Неверный ключ операции")
