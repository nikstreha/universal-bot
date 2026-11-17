from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class InstallationId(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (0 < len(self.value) <= 100):
            raise InvalidMetadataError("Неверный идентификатор установки")
