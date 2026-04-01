from datetime import UTC, datetime
from typing import Self

from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.chat.tg_chat_id import TgChatId
from universal_bot.domain.value_object.user.id import UserId


class Chat(Entity[ChatId]):
    def __init__(
        self,
        *,
        id_: ChatId,
        tg_chat_id: TgChatId,
        user_id: UserId,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id_=id_)
        self.tg_chat_id = tg_chat_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create(
        cls,
        id_: ChatId,
        tg_chat_id: TgChatId,
        user_id: UserId,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id_=id_,
            tg_chat_id=tg_chat_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )

    def _touch(self) -> None:
        self.updated_at = datetime.now(UTC)
