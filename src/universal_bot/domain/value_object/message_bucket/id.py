from dataclasses import dataclass

from universal_bot.domain.exception import DomainError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class MessageBucketId(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if ":" not in self.value:
            raise DomainError("MessageBucketId must be in '{chat_id}:{seq}' format")
