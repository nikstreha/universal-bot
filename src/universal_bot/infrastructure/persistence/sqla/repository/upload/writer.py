from collections.abc import Sequence

from sqlalchemy import select

from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.upload import Upload
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.upload import upload_table
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAUploadWriter(IUploadWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: UploadId) -> Upload | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Upload, key_raw)

    async def list_by_state_expiring_before(
        self, *, state: UploadState, expires_before: Timestamp
    ) -> list[Upload]:
        state_raw = convert_to_primitive(state)
        expires_before_raw = convert_to_primitive(expires_before)
        statement = select(Upload)
        statement = statement.where(
            upload_table.c.state == state_raw,
            upload_table.c.expires_at < expires_before_raw,
        )
        return list(await self._session.scalars(statement))

    async def list_by_states(self, *, states: Sequence[UploadState]) -> list[Upload]:
        states_raw = convert_to_primitive(states)
        statement = select(Upload)
        statement = statement.where(upload_table.c.state.in_(states_raw))
        return list(await self._session.scalars(statement))

    async def find_by_owner_id_and_operation_key(
        self, *, owner_id: TelegramUserId, operation_key: IdempotencyKey
    ) -> Upload | None:
        owner_id_raw = convert_to_primitive(owner_id)
        operation_key_raw = convert_to_primitive(operation_key)
        statement = select(Upload)
        statement = statement.where(
            upload_table.c.owner_id == owner_id_raw,
            upload_table.c.operation_key == operation_key_raw,
        )
        return (await self._session.scalars(statement.limit(1))).first()

    async def list_by_states_expiring_after(
        self, *, states: Sequence[UploadState], expires_after: Timestamp
    ) -> list[Upload]:
        states_raw = convert_to_primitive(states)
        expires_after_raw = convert_to_primitive(expires_after)
        statement = select(Upload)
        statement = statement.where(
            upload_table.c.state.in_(states_raw),
            upload_table.c.expires_at > expires_after_raw,
        )
        return list(await self._session.scalars(statement))

    async def add(self, *, entity: Upload) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def list_by_owner_and_states(
        self, *, owner_id: TelegramUserId, states: Sequence[UploadState]
    ) -> list[Upload]:
        owner_id_raw = convert_to_primitive(owner_id)
        states_raw = convert_to_primitive(states)
        statement = select(Upload)
        statement = statement.where(
            upload_table.c.owner_id == owner_id_raw,
            upload_table.c.state.in_(states_raw),
        )
        return list(await self._session.scalars(statement))
