from enum import Enum


class UserRoles(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEMP_ADMIN = "temp_admin"
    USER = "user"
    TEMP_USER = "temp_user"
    OTHER = "other"

    @classmethod
    def is_admin(cls, role: "UserRoles") -> bool:
        return role in (cls.ADMIN, cls.TEMP_ADMIN, cls.SUPERADMIN)
