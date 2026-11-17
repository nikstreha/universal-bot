from universal_bot.domain.entity.common import Entity
from universal_bot.domain.exception.common import InvalidMetadataError
from universal_bot.domain.exception.session import (
    SessionExpiredError,
    SessionRevokedError,
)
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class Session(Entity[SessionId]):
    _id: SessionId
    user_id: TelegramUserId
    token_hash: TokenHash
    installation_id: InstallationId
    device_name: DeviceName
    created_at: Timestamp
    last_seen_at: Timestamp
    expires_at: Timestamp
    absolute_expires_at: Timestamp
    revoked_at: Timestamp | None

    def __init__(
        self,
        *,
        id_: SessionId,
        user_id: TelegramUserId,
        token_hash: TokenHash,
        installation_id: InstallationId,
        device_name: DeviceName,
        created_at: Timestamp,
        last_seen_at: Timestamp,
        expires_at: Timestamp,
        absolute_expires_at: Timestamp,
        revoked_at: Timestamp | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.user_id = user_id
        self.token_hash = token_hash
        self.installation_id = installation_id
        self.device_name = device_name
        self.created_at = created_at
        self.last_seen_at = last_seen_at
        self.expires_at = expires_at
        self.absolute_expires_at = absolute_expires_at
        self.revoked_at = revoked_at

    @classmethod
    def create(
        cls,
        *,
        id_: SessionId,
        user_id: TelegramUserId,
        token_hash: TokenHash,
        installation_id: InstallationId,
        device_name: DeviceName,
        at: Timestamp,
        idle_seconds: int,
        max_seconds: int,
    ) -> Session:
        if idle_seconds <= 0 or max_seconds <= 0:
            raise InvalidMetadataError("Неверный срок сессии")
        return cls(
            id_=id_,
            user_id=user_id,
            token_hash=token_hash,
            installation_id=installation_id,
            device_name=device_name,
            created_at=at,
            last_seen_at=at,
            expires_at=at.after(min(idle_seconds, max_seconds)),
            absolute_expires_at=at.after(max_seconds),
        )

    def validate(self, at: Timestamp) -> None:
        if self.revoked_at is not None:
            raise SessionRevokedError()
        if min(self.expires_at.value, self.absolute_expires_at.value) <= at.value:
            raise SessionExpiredError()

    def touch(self, at: Timestamp, idle_seconds: int) -> None:
        self.validate(at)
        if at.value - self.last_seen_at.value >= 60:
            self.last_seen_at = at
            self.expires_at = Timestamp(
                min(at.value + idle_seconds, self.absolute_expires_at.value)
            )

    def revoke(self, at: Timestamp) -> None:
        if self.revoked_at is None:
            self.revoked_at = at
