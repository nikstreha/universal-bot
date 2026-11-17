from dataclasses import dataclass

from universal_bot.domain.exception.common import InvalidIdentifierError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TelegramUpdateId(ValueObject):
    value: int

    def __post_init__(self):
        if type(self.value) is not int or self.value < 0:
            raise InvalidIdentifierError("Неверный идентификатор обновления")
