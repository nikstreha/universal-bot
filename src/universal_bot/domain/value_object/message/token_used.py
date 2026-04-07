from dataclasses import dataclass

from universal_bot.domain.exception import DomainError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TokenUsed(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise DomainError("Token used must be non-negative")
