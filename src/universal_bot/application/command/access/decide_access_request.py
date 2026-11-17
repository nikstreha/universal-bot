import logging

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_grant.writer import (
    IAccessGrantWriter,
)
from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.access_grant import AccessGrant
from universal_bot.domain.entity.access_request import AccessRequest
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class DecideAccessRequestInteractor:
    def __init__(
        self,
        *,
        access_grant_writer: IAccessGrantWriter,
        access_policy: AccessPolicy,
        access_request_writer: IAccessRequestWriter,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._access_grant_writer = access_grant_writer
        self._access_policy = access_policy
        self._access_request_writer = access_request_writer
        self._clock = clock
        self._uow = uow

    async def __call__(
        self, *, actor_id: int, request_id: str, approved: bool
    ) -> AccessRequest:
        await self._access_policy.require_admin(actor_id=actor_id)
        async with self._uow:
            request = await self._access_request_writer.find_by_id(
                key=AccessRequestId(request_id)
            )
            ensure(request, NotFoundError, "Запрос не найден")
            request.decide(
                approved, TelegramUserId(actor_id), Timestamp(self._clock.now())
            )
            if approved and (
                not await self._access_grant_writer.find_by_id(key=request.user_id)
            ):
                await self._access_grant_writer.add(
                    entity=AccessGrant(
                        user_id=request.user_id,
                        added_at=Timestamp(self._clock.now()),
                        added_by=TelegramUserId(actor_id),
                    )
                )
        logging.getLogger(__name__).info(
            "Access request decided",
            extra={
                "event": "admin_action",
                "actor_id": actor_id,
                "target_id": request.user_id.value,
                "operation": "approve_request" if approved else "reject_request",
            },
        )
        return request
