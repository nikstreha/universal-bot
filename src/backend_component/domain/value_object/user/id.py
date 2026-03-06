from dataclasses import dataclass

from backend_component.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: int
