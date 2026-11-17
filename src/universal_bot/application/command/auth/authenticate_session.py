import re

from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import AuthRequiredError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.session.reader import (
    ISessionReader,
)
from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.session import Session
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AuthenticateSessionInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        policy: Policy,
        secrets: ISecrets,
        session_reader: ISessionReader,
        session_writer: ISessionWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._policy = policy
        self._secrets = secrets
        self._session_reader = session_reader
        self._session_writer = session_writer
        self._uow = uow

    async def __call__(self, *, secret: str) -> SessionQueryModel:
        ensure(
            re.fullmatch("[A-Za-z0-9_-]{43}", secret),
            AuthRequiredError,
            "Войдите через Telegram",
        )
        snapshot = await self._session_reader.find_by_token_hash(
            token_hash=TokenHash(self._secrets.hash(secret))
        )
        ensure(snapshot, AuthRequiredError, "Войдите через Telegram")
        Session(
            user_id=TelegramUserId(snapshot.user_id),
            token_hash=TokenHash(snapshot.token_hash),
            installation_id=InstallationId(snapshot.installation_id),
            device_name=DeviceName(snapshot.device_name),
            created_at=Timestamp(snapshot.created_at),
            last_seen_at=Timestamp(snapshot.last_seen_at),
            expires_at=Timestamp(snapshot.expires_at),
            absolute_expires_at=Timestamp(snapshot.absolute_expires_at),
            revoked_at=Timestamp.from_raw(snapshot.revoked_at),
            id_=SessionId(snapshot.id),
        ).validate(Timestamp(self._clock.now()))
        await self._access_policy.require_access(user_id=snapshot.user_id)
        if snapshot.last_seen_at >= self._clock.now() - 60:
            return snapshot
        async with self._uow:
            session = await self._session_writer.find_by_id(key=SessionId(snapshot.id))
            ensure(session, AuthRequiredError, "Войдите через Telegram")
            session.validate(Timestamp(self._clock.now()))
            await self._access_policy.require_access(user_id=session.user_id.value)
            session.touch(
                Timestamp(self._clock.now()), self._policy.session_idle_seconds
            )
            return SessionQueryModel(**session.to_dict())
