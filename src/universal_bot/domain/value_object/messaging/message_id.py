from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TelegramMessageId(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value <= 0:
            raise InvalidMetadataError("Неверный идентификатор сообщения")
