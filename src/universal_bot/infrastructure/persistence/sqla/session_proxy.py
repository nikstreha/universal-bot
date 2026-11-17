from typing import Any

from universal_bot.infrastructure.persistence.sqla.sqla_uow import SQLAUnitOfWork


class SessionProxy:
    def __init__(self, uow: SQLAUnitOfWork) -> None:
        self._uow = uow

    def __getattr__(self, name: str) -> Any:
        return getattr(self._uow.session, name)
