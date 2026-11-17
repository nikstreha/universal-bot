from sqlalchemy import select

from universal_bot.application.port.persistence.repository.upload_part.writer import (
    IUploadPartWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.upload_part import UploadPart
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_id import UploadPartId
from universal_bot.infrastructure.persistence.sqla.table.upload_part import (
    upload_part_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAUploadPartWriter(IUploadPartWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def list_by_upload_id(self, *, upload_id: UploadId) -> list[UploadPart]:
        upload_id_raw = convert_to_primitive(upload_id)
        statement = select(UploadPart)
        statement = statement.where(upload_part_table.c.upload_id == upload_id_raw)
        statement = statement.order_by(upload_part_table.c.part_index)
        return list(await self._session.scalars(statement))

    async def find_by_id(self, *, key: UploadPartId) -> UploadPart | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(UploadPart, key_raw)

    async def delete(self, *, entity: UploadPart) -> None:
        await self._session.delete(entity)

    async def add(self, *, entity: UploadPart) -> None:
        self._session.add(entity)
        await self._session.flush()
