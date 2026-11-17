from abc import ABC, abstractmethod

from universal_bot.domain.entity.audit_event import AuditEvent


class IAuditEventWriter(ABC):
    @abstractmethod
    async def add(self, *, entity: AuditEvent) -> None: ...
