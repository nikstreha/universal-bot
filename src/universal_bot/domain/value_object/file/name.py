from dataclasses import dataclass

from universal_bot.domain.exception.file import InvalidFileNameError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class FileName(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if (
            not self.value.strip()
            or len(self.value) > 255
            or any(c in self.value for c in ("/", "\\", "\x00", "\r", "\n"))
        ):
            raise InvalidFileNameError()
