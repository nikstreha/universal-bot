from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("ValueObject cannot be instantiated directly")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field")
        return object.__new__(cls)

    @classmethod
    def from_raw(cls, *values: Any) -> Self | None:
        if all(value is None for value in values):
            return None
        if len(values) == 1 and isinstance(values[0], cls):
            return values[0]
        return cls(*values)

    def to_dict(self) -> Any:
        from universal_bot.domain.common.util import convert_to_primitive

        visible = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.repr
        }
        if not visible:
            return "<hidden>"
        if len(visible) == 1:
            return convert_to_primitive(next(iter(visible.values())))
        return {name: convert_to_primitive(value) for name, value in visible.items()}

    def __composite_values__(self) -> tuple:
        from universal_bot.domain.common.util import convert_to_primitive

        return tuple(
            convert_to_primitive(getattr(self, field.name)) for field in fields(self)
        )

    def __repr__(self) -> str:
        visible = [
            f"{field.name}={getattr(self, field.name)!r}"
            for field in fields(self)
            if field.repr
        ]
        return (
            f"{type(self).__name__}("
            + (", ".join(visible) if visible else "<hidden>")
            + ")"
        )
