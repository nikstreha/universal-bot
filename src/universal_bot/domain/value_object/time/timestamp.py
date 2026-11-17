from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Timestamp(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value < 0:
            raise InvalidMetadataError("Неверное время")

    def after(self, seconds: int) -> Timestamp:
        if seconds < 0:
            raise InvalidMetadataError("Неверная длительность")
        return Timestamp(self.value + seconds)
