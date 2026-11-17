from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class ObjectKey(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (
            bool(self.value)
            and len(self.value) <= 1024
            and not self.value.startswith("/")
            and not any(part in ("", ".", "..") for part in self.value.split("/"))
            and not any(ord(c) < 32 for c in self.value)
        ):
            raise InvalidMetadataError("Неверный ключ объекта")
