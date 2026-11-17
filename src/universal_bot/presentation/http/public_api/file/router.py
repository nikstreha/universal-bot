from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Query, Response
from starlette.responses import StreamingResponse

from universal_bot.application.command.access.apply_rate_limit import (
    ApplyRateLimitInteractor,
)
from universal_bot.application.command.file.request_file_verification import (
    RequestFileVerificationInteractor,
)
from universal_bot.application.command.file.restore_file import RestoreFileInteractor
from universal_bot.application.command.file.trash_file import TrashFileInteractor
from universal_bot.application.query.file.get_file import GetFileInteractor
from universal_bot.application.query.file.get_file_catalog import (
    GetFileCatalogInteractor,
)
from universal_bot.application.query.file.get_file_date_list import (
    GetFileDateListInteractor,
)
from universal_bot.application.query.file.get_file_verification import (
    GetFileVerificationInteractor,
)
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.presentation.http.public_api.auth.dependencies import session
from universal_bot.presentation.http.public_api.common.schema import PageResponse
from universal_bot.presentation.http.public_api.file.response import FileResponseFactory
from universal_bot.presentation.http.public_api.file.schema import (
    FileDateGroupResponse,
    FileResponse,
    VerificationResponse,
)


def create_file_router() -> APIRouter:
    router = APIRouter(prefix="/files", tags=["file"])

    @router.get("/dates")
    @inject
    async def dates(
        state: str = "active",
        collection: str = "",
        kind: str = "",
        q: str = Query(default="", max_length=200),
        cursor: str = "",
        limit: int = Query(default=31, ge=1, le=100),
        current: SessionQueryModel = Depends(session),
        *,
        get_file_date_list: FromDishka[GetFileDateListInteractor],
    ) -> PageResponse[FileDateGroupResponse]:
        page = await get_file_date_list(
            user_id=current.user_id,
            state=state,
            collection=collection,
            kind=kind,
            q=q,
            cursor=cursor,
            limit=limit,
        )
        return PageResponse(
            items=[FileDateGroupResponse.model_validate(row) for row in page.items],
            next_cursor=page.next_cursor,
        )

    @router.get("")
    @inject
    async def files(
        state: str = "active",
        collection: str = "",
        kind: str = "",
        q: str = Query(default="", max_length=200),
        date_from: str = "",
        date_to: str = "",
        cursor: str = "",
        limit: int = Query(default=50, ge=1, le=100),
        current: SessionQueryModel = Depends(session),
        *,
        get_file_catalog: FromDishka[GetFileCatalogInteractor],
    ) -> PageResponse[FileResponse]:
        page = await get_file_catalog(
            user_id=current.user_id,
            state=state,
            collection=collection,
            kind=kind,
            q=q,
            date_from=date_from,
            date_to=date_to,
            cursor=cursor,
            limit=limit,
        )
        return PageResponse(
            items=[FileResponse.from_file(row) for row in page.items],
            next_cursor=page.next_cursor,
        )

    @router.get("/{file_id}")
    @inject
    async def detail(
        file_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        get_file: FromDishka[GetFileInteractor],
    ) -> FileResponse:
        return FileResponse.from_file(
            await get_file(user_id=current.user_id, file_id=str(file_id))
        )

    @router.get("/{file_id}/content")
    @inject
    async def content(
        file_id: UUID,
        disposition: str = "attachment",
        authorization: str = Header(default=""),
        range: str = Header(default=""),
        if_range: str = Header(default=""),
        current: SessionQueryModel = Depends(session),
        *,
        file_response: FromDishka[FileResponseFactory],
        get_file: FromDishka[GetFileInteractor],
    ) -> StreamingResponse:
        row = await get_file(user_id=current.user_id, file_id=str(file_id))
        return await file_response(
            row,
            authorization,
            range if not if_range or if_range == '"' + row.sha256 + '"' else "",
            disposition == "inline",
        )

    @router.get("/{file_id}/thumbnail")
    @inject
    async def thumbnail(
        file_id: UUID,
        authorization: str = Header(default=""),
        current: SessionQueryModel = Depends(session),
        *,
        file_response: FromDishka[FileResponseFactory],
        get_file: FromDishka[GetFileInteractor],
    ) -> StreamingResponse:
        return await file_response(
            await get_file(user_id=current.user_id, file_id=str(file_id)),
            authorization,
            thumbnail=True,
        )

    @router.post("/{file_id}/trash")
    @inject
    async def trash(
        file_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        trash_file: FromDishka[TrashFileInteractor],
    ) -> FileResponse:
        return FileResponse.from_file(
            await trash_file(user_id=current.user_id, file_id=str(file_id))
        )

    @router.post("/{file_id}/restore")
    @inject
    async def restore(
        file_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        restore_file: FromDishka[RestoreFileInteractor],
    ) -> FileResponse:
        return FileResponse.from_file(
            await restore_file(user_id=current.user_id, file_id=str(file_id))
        )

    @router.post("/{file_id}/verifications")
    @inject
    async def verify(
        file_id: UUID,
        response: Response,
        idempotency_key: str = Header(min_length=1, max_length=120),
        current: SessionQueryModel = Depends(session),
        *,
        apply_rate_limit: FromDishka[ApplyRateLimitInteractor],
        request_file_verification: FromDishka[RequestFileVerificationInteractor],
    ) -> VerificationResponse:
        await apply_rate_limit(key=f"verify:{current.user_id}", maximum=20)
        row = await request_file_verification(
            user_id=current.user_id, file_id=str(file_id), key=idempotency_key
        )
        response.status_code = 200 if row.state in ("succeeded", "failed") else 202
        return VerificationResponse.from_verification(row)

    @router.get("/{file_id}/verifications/{verification_id}")
    @inject
    async def verification(
        file_id: UUID,
        verification_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        get_file_verification: FromDishka[GetFileVerificationInteractor],
    ) -> VerificationResponse:
        return VerificationResponse.from_verification(
            await get_file_verification(
                user_id=current.user_id,
                file_id=str(file_id),
                verification_id=str(verification_id),
            )
        )

    return router
