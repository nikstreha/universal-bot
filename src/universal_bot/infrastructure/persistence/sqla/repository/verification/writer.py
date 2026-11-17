from sqlalchemy import select

from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.verification import Verification
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.verification.id import VerificationId
from universal_bot.infrastructure.persistence.sqla.table.verification import (
    verification_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAVerificationWriter(IVerificationWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: VerificationId) -> Verification | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Verification, key_raw)

    async def list_by_file_id(self, *, file_id: StoredFileId) -> list[Verification]:
        file_id_raw = convert_to_primitive(file_id)
        statement = select(Verification)
        statement = statement.where(verification_table.c.file_id == file_id_raw)
        return list(await self._session.scalars(statement))

    async def delete(self, *, entity: Verification) -> None:
        await self._session.delete(entity)

    async def find_by_file_id_and_operation_key(
        self, *, file_id: StoredFileId, operation_key: IdempotencyKey
    ) -> Verification | None:
        file_id_raw = convert_to_primitive(file_id)
        operation_key_raw = convert_to_primitive(operation_key)
        statement = select(Verification)
        statement = statement.where(
            verification_table.c.file_id == file_id_raw,
            verification_table.c.operation_key == operation_key_raw,
        )
        return (await self._session.scalars(statement.limit(1))).first()

    async def add(self, *, entity: Verification) -> None:
        self._session.add(entity)
        await self._session.flush()
