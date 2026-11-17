from sqlalchemy import select

from universal_bot.application.port.persistence.repository.verification.reader import (
    IVerificationReader,
)
from universal_bot.application.query_model.verification import VerificationQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.verification.id import VerificationId
from universal_bot.infrastructure.persistence.sqla.table.verification import (
    verification_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAVerificationReader(IVerificationReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: VerificationId) -> VerificationQueryModel | None:
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
        return VerificationQueryModel(**row) if row else None
