from sqlalchemy import select

from universal_bot.application.port.persistence.repository.upload.reader import (
    IUploadReader,
)
from universal_bot.application.query_model.upload import UploadQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.infrastructure.persistence.sqla.table.upload import (
    upload_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAUploadReader(IUploadReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: UploadId) -> UploadQueryModel | None:
        key_raw = convert_to_primitive(key)
        row = (
            (
                await self._session.execute(
                    select(table).where(table.c.id == key_raw).limit(1)
                )
            )
            .mappings()
            .first()
        )
        return UploadQueryModel(**row) if row else None
