from dataclasses import dataclass

from universal_bot.domain.exception.user import InvalidTelegramUserIdError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TelegramUserId(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or not 0 < self.value < 2**63:
            raise InvalidTelegramUserIdError()
