from universal_bot.application.exception.common import AccessAlreadyGrantedError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.access_request import AccessRequest
from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName


class RequestAccessInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        access_request_writer: IAccessRequestWriter,
        clock: IClock,
        secrets: ISecrets,
        uow: IUnitOfWork,
        user_writer: IUserWriter,
    ) -> None:
        self._access_policy = access_policy
        self._access_request_writer = access_request_writer
        self._clock = clock
        self._secrets = secrets
        self._uow = uow
        self._user_writer = user_writer

    async def __call__(
        self, *, user_id: int, source: str
    ) -> tuple[AccessRequest, bool]:
        async with self._uow:
            ensure(
                not await self._access_policy.allowed(user_id=user_id),
                AccessAlreadyGrantedError,
                "Доступ уже открыт",
            )
            user = await self._user_writer.find_by_id(key=TelegramUserId(user_id))
            user_at = Timestamp(self._clock.now())
            if user is None:
                user = User(
                    id_=TelegramUserId(user_id),
                    name=UserName(""),
                    created_at=user_at,
                    last_seen_at=user_at,
                )
                await self._user_writer.add(entity=user)
            else:
                user.touch(UserName(""), user_at)
            request = await self._access_request_writer.find_by_user_id(
                user_id=TelegramUserId(user_id)
            )
            created = request is None
            if created:
                request = AccessRequest(
                    id_=AccessRequestId(self._secrets.identity()),
                    user_id=TelegramUserId(user_id),
                    source=AccessSource(source),
                    created_at=Timestamp(self._clock.now()),
                )
                await self._access_request_writer.add(entity=request)
            return (request, created)
