import re
from dataclasses import dataclass

from universal_bot.domain.exception.auth import InvalidLoginError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class LoginCode(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (re.fullmatch(r"[0-9]{6}", self.value) is not None):
            raise InvalidLoginError("Неверный код входа")
