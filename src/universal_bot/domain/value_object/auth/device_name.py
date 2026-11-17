from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class DeviceName(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (
            0 < len(self.value) <= 100 and not any(ord(c) < 32 for c in self.value)
        ):
            raise InvalidMetadataError("Неверное имя устройства")
