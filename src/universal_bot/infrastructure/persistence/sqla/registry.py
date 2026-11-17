from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

NAMING_CONVENTION: Final[Mapping[str, str]] = MappingProxyType(
    {
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
metadata = MetaData(naming_convention=NAMING_CONVENTION)
mapping_registry = registry(metadata=metadata)
