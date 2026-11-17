from typing import Any, ClassVar, Self

from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.common import ValueObject


class Entity[T: ValueObject]:
    _identity_field: ClassVar[str | None] = "id"

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is Entity:
            raise TypeError("Entity cannot be instantiated directly")
        return object.__new__(cls)

    def __init__(self, *, id_: T) -> None:
        self._id = id_

    @property
    def id_(self) -> T:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id_ == other.id_

    def __hash__(self) -> int:
        return hash((type(self), self.id_))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id_={self.id_!r})"

    def to_dict(self) -> dict[str, Any]:
        result = (
            {self._identity_field: convert_to_primitive(self.id_)}
            if self._identity_field
            else {}
        )
        for name in type(self).__annotations__:
            if not name.startswith("_"):
                result[name] = convert_to_primitive(getattr(self, name))
        return result
