from dataclasses import dataclass

from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class MessageId(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Message ID must be greater than 0")
