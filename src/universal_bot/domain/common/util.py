from dataclasses import fields
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from universal_bot.domain.value_object.common import ValueObject


def convert_to_primitive(value):
    if isinstance(value, ValueObject):
        own = fields(value)
        if len(own) == 1:
            return convert_to_primitive(getattr(value, own[0].name))
        return tuple(convert_to_primitive(getattr(value, field.name)) for field in own)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (tuple, list)):
        return tuple(convert_to_primitive(item) for item in value)
    return value
