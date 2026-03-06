from enum import StrEnum
from typing import Any


class UserRole(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEMP_ADMIN = "temp_admin"
    USER = "user"
    TEMP_USER = "temp_user"
    BANNED = "banned"
    OTHER = "other"

    @property
    def weight(self) -> int:
        match self:
            case UserRole.SUPERADMIN:
                return 30
            case UserRole.ADMIN:
                return 20
            case UserRole.USER:
                return 10
            case UserRole.TEMP_ADMIN:
                return 15
            case UserRole.TEMP_USER:
                return 5
            case UserRole.BANNED:
                return -10
            case UserRole.OTHER:
                return 0
            
    def is_admin(self) -> bool:
        return self.weight >= self.TEMP_ADMIN.weight
    
    def is_permitted(self) -> bool:
        return self.weight >= self.TEMP_USER.weight

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, UserRole):
            return NotImplemented
        return self.weight > other.weight

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, UserRole):
            return NotImplemented
        return self.weight < other.weight

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, UserRole):
            return NotImplemented
        return self.weight >= other.weight

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, UserRole):
            return NotImplemented
        return self.weight <= other.weight
