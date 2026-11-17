from abc import ABC, abstractmethod

from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class ISessionReader(ABC):
    @abstractmethod
    async def find_by_token_hash(
        self, *, token_hash: TokenHash
    ) -> SessionQueryModel | None: ...

    @abstractmethod
    async def list_by_user_id(
        self, *, user_id: TelegramUserId, revoked_at: Timestamp
    ) -> list[SessionQueryModel]: ...
