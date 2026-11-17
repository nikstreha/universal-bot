from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidRangeError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class PartIndex(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if not (type(self.value) is int and self.value >= 0):
            raise InvalidRangeError("Неверный номер части")
