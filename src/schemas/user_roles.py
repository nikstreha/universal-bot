from enum import Enum


class AdminRoles(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEMP_ADMIN = "temp_admin"


class UserRoles(AdminRoles):
    USER = "user"
    TEMP_USER = "temp_user"
    OTHER = "other"