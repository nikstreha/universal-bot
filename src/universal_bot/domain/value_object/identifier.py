from dataclasses import dataclass
from uuid import UUID

from universal_bot.domain.exception.common import InvalidIdentifierError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UUIDIdentifier(ValueObject):
    value: UUID

    def __post_init__(self) -> None:
        try:
            value = self.value if isinstance(self.value, UUID) else UUID(self.value)
        except (ValueError, TypeError, AttributeError) as exc:
            raise InvalidIdentifierError("Неверный идентификатор") from exc
        if value.int == 0:
            raise InvalidIdentifierError("Пустой идентификатор")
        object.__setattr__(self, "value", value)
