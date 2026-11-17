from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class PartSize(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if not (type(self.value) is int and 5 * 1024**2 <= self.value <= 32 * 1024**2):
            raise InvalidMetadataError("Размер части должен быть от 5 до 32 МиБ")
