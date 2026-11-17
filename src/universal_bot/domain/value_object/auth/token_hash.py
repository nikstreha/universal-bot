import re
from dataclasses import dataclass, field

from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TokenHash(ValueObject):
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if re.fullmatch(r"[a-f0-9]{64}", self.value) is None:
            raise InvalidMetadataError("Неверный хеш сессии")
