from universal_bot.application.port.persistence.repository.audit_event.writer import (
    IAuditEventWriter,
)
from universal_bot.domain.entity.audit_event import AuditEvent
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAuditEventWriter(IAuditEventWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def add(self, *, entity: AuditEvent) -> None:
        self._session.add(entity)
        await self._session.flush()
