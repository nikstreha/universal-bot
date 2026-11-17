from dataclasses import dataclass
from datetime import date

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class ArchiveDate(ValueObject):
    value: date

    def __post_init__(self) -> None:
        try:
            value = (
                self.value
                if type(self.value) is date
                else date.fromisoformat(self.value)
            )
        except (TypeError, ValueError) as exc:
            raise InvalidMetadataError("Неверная дата архива") from exc
        object.__setattr__(self, "value", value)
