from enum import StrEnum
from typing import NewType

from sqlalchemy import String, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession

ReaderSession = NewType("ReaderSession", AsyncSession)
WriterSession = NewType("WriterSession", AsyncSession)


class EnumStringType[T: StrEnum](TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_class: type[T]) -> None:
        super().__init__()
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        return None if value is None else self.enum_class(value).value

    def process_result_value(self, value, dialect):
        return None if value is None else self.enum_class(value)
