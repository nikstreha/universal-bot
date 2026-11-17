from sqlalchemy import select

from universal_bot.application.port.persistence.repository.upload_part.reader import (
    IUploadPartReader,
)
from universal_bot.application.query_model.upload_part import UploadPartQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.infrastructure.persistence.sqla.table.upload_part import (
    upload_part_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAUploadPartReader(IUploadPartReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def list_by_upload_id(
        self, *, upload_id: UploadId
    ) -> list[UploadPartQueryModel]:
        upload_id_raw = convert_to_primitive(upload_id)
        statement = select(table)
        statement = statement.where(table.c.upload_id == upload_id_raw)
        statement = statement.order_by(table.c.part_index)
        return [
            UploadPartQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
