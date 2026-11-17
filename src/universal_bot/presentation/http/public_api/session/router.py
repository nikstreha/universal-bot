from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from universal_bot.application.command.auth.revoke_session import (
    RevokeSessionInteractor,
)
from universal_bot.application.query.auth.get_session_list import (
    GetSessionListInteractor,
)
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.presentation.http.public_api.auth.dependencies import session
from universal_bot.presentation.http.public_api.session.schema import (
    SessionCollectionResponse,
    SessionResponse,
)


def create_session_router() -> APIRouter:
    router = APIRouter(prefix="/sessions", tags=["session"])

    @router.get("")
    @inject
    async def sessions(
        current: SessionQueryModel = Depends(session),
        *,
        get_session_list: FromDishka[GetSessionListInteractor],
    ) -> SessionCollectionResponse:
        return SessionCollectionResponse(
            items=[
                SessionResponse(
                    id=row.id,
                    device_name=row.device_name,
                    created_at=row.created_at,
                    last_seen_at=row.last_seen_at,
                    expires_at=row.expires_at,
                    is_current=row.id == current.id,
                )
                for row in await get_session_list(user_id=current.user_id)
            ]
        )

    @router.delete("/{session_id}", status_code=204)
    @inject
    async def revoke_session(
        session_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        revoke_session: FromDishka[RevokeSessionInteractor],
    ) -> None:
        await revoke_session(user_id=current.user_id, session_id=str(session_id))

    return router
