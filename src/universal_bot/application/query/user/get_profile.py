from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.query_model.profile import (
    ProfileQueryModel,
    StorageLimitsQueryModel,
)
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetProfileInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        policy: Policy,
        stored_file_reader: IStoredFileReader,
        user_reader: IUserReader,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._policy = policy
        self._stored_file_reader = stored_file_reader
        self._user_reader = user_reader

    async def __call__(self, *, user_id: int) -> ProfileQueryModel:
        await self._access_policy.require_access(user_id=user_id)
        user = await self._user_reader.find_by_id(key=TelegramUserId(user_id))
        volumes = await self._stored_file_reader.get_volumes(
            owner_id=TelegramUserId(user_id)
        )
        return ProfileQueryModel(
            id=str(user_id),
            name=user.name,
            is_admin=user_id == self._policy.admin_id,
            volumes=volumes,
            archive_date=self._clock.archive_date(self._policy.archive_timezone),
            archive_timezone=self._policy.archive_timezone,
            limits=StorageLimitsQueryModel(
                max_file_bytes=self._policy.max_file_bytes,
                upload_part_bytes=self._policy.part_bytes,
                max_open_uploads=self._policy.max_open_uploads,
                upload_idle_ttl_seconds=self._policy.upload_idle_seconds,
                trash_retention_days=self._policy.trash_retention_seconds // 86400,
            ),
        )
