from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class DeduplicationKey(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value, str)
            or len(self.value) > 200
            or (True and not self.value)
        ):
            raise InvalidMetadataError("Недопустимое значение DeduplicationKey")
