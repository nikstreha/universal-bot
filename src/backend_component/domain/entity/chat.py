from datetime import UTC, datetime
from typing import Self

from backend_component.domain.entity.common import Entity
from backend_component.domain.value_object.user.id import UserId
from backend_component.domain.value_object.message.message import Message
from backend_component.domain.value_object.chat.id import ChatId


class MyChat(Entity[ChatId]):
    def __init__(
        self,
        *,
        id_: ChatId,
        user_id: UserId,
        created_at: datetime,
        updated_at: datetime,
        messages: list[Message] | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id
        self.messages = messages

    @classmethod
    def create(
        cls,
        id_: ChatId,
        user_id: UserId,
        messages: list[Message],
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id_=id_,
            user_id=user_id,
            messages=messages,
            created_at=now,
            updated_at=now,
        )

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
