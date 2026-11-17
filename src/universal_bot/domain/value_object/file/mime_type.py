import re
from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class MimeType(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (
            0 < len(self.value) <= 150
            and re.fullmatch(r"[a-zA-Z0-9!#$&^_.+-]+/[a-zA-Z0-9!#$&^_.+-]+", self.value)
            is not None
        ):
            raise InvalidMetadataError("Неверный тип файла")
