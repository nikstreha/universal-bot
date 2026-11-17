from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class ArchiveTimezone(ValueObject):
    value: str

    def __post_init__(self) -> None:
        try:
            ZoneInfo(self.value)
        except (ValueError, ZoneInfoNotFoundError) as exc:
            raise InvalidMetadataError("Неверный часовой пояс архива") from exc
