import re
from dataclasses import dataclass

from universal_bot.domain.exception.file import InvalidSHA256DigestError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class SHA256Digest(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if re.fullmatch("[a-f0-9]{64}", self.value) is None:
            raise InvalidSHA256DigestError()
