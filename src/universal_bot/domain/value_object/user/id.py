from dataclasses import dataclass

from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("User ID must be greater than 0")
