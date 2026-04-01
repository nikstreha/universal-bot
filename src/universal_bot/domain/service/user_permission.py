from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.domain.exception import (
    CannotModifySuperadminError,
    InsufficientRoleWeightError,
)


class UserPermissionService:
    @staticmethod
    def ensure_can_ban(actor: User, target: User) -> None:
        if target.role == UserRole.SUPERADMIN:
            raise CannotModifySuperadminError("Cannot ban a superadmin.")
        if not actor.role > target.role:
            raise InsufficientRoleWeightError(
                f"Actor role {actor.role} cannot ban target role {target.role}."
            )

    @staticmethod
    def ensure_can_change_role(actor: User, target: User, new_role: UserRole) -> None:
        if target.role == UserRole.SUPERADMIN:
            raise CannotModifySuperadminError("Cannot change superadmin's role.")
        if not actor.role > target.role:
            raise InsufficientRoleWeightError(
                f"Actor role {actor.role} cannot modify target role {target.role}."
            )
        if not actor.role > new_role:
            raise InsufficientRoleWeightError(
                f"Actor role {actor.role} cannot assign role {new_role}."
            )
