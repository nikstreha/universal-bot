from dataclasses import dataclass

from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class MessageContent(ValueObject):
    value: str
