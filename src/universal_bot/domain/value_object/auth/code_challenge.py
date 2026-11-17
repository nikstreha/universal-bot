import re
from dataclasses import dataclass

from universal_bot.domain.exception.auth import InvalidLoginError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class CodeChallenge(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not (re.fullmatch(r"[A-Za-z0-9_-]{43}", self.value) is not None):
            raise InvalidLoginError("Неверное подтверждение попытки")
