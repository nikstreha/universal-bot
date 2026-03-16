from datetime import UTC, datetime
from typing import Self

from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.domain.value_object.user.id import UserId
from universal_bot.domain.value_object.user.username import UserName


class User(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        role: UserRole,
        touched_at: datetime,
        username: UserName | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.role = role
        self.touched_at = touched_at

    @classmethod
    def create(
        cls,
        id_: UserId,
        role: UserRole,
        username: UserName | None = None,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id_=id_,
            role=role,
            username=username,
            touched_at=now,
        )

    def change_role(self, new_role: UserRole) -> None:
        self.role = new_role
        self._touch()

    def _touch(self) -> None:
        self.touched_at = datetime.now(UTC)
