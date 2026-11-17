from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Request, Response

from universal_bot.application.command.upload.cancel_upload import (
    CancelUploadInteractor,
)
from universal_bot.application.command.upload.complete_upload import (
    CompleteUploadInteractor,
)
from universal_bot.application.command.upload.create_upload import (
    CreateUploadInteractor,
)
from universal_bot.application.command.upload.receive_upload_part import (
    ReceiveUploadPartInteractor,
)
from universal_bot.application.dto.upload.create_upload import CreateUploadRequestDTO
from universal_bot.application.exception.common import PartTooLargeError
from universal_bot.application.query.upload.get_upload import GetUploadInteractor
from universal_bot.application.query.upload.get_upload_part_size import (
    GetUploadPartSizeInteractor,
)
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidRangeError
from universal_bot.presentation.http.public_api.auth.dependencies import session
from universal_bot.presentation.http.public_api.upload.schema import (
    UploadBody,
    UploadResponse,
)


def create_upload_router() -> APIRouter:
    router = APIRouter(prefix="/uploads", tags=["upload"])

    @router.post("")
    @inject
    async def create_upload(
        body: UploadBody,
        response: Response,
        idempotency_key: str = Header(min_length=1, max_length=120),
        current: SessionQueryModel = Depends(session),
        *,
        create_upload: FromDishka[CreateUploadInteractor],
        get_upload: FromDishka[GetUploadInteractor],
    ) -> UploadResponse:
        upload_id, created = await create_upload(
            request=CreateUploadRequestDTO(
                user_id=current.user_id,
                operation_key=idempotency_key,
                **body.model_dump(),
            )
        )
        response.status_code = 201 if created else 200
        return UploadResponse.from_upload(
            await get_upload(user_id=current.user_id, upload_id=upload_id)
        )

    @router.get("/{upload_id}")
    @inject
    async def upload(
        upload_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        get_upload: FromDishka[GetUploadInteractor],
    ) -> UploadResponse:
        return UploadResponse.from_upload(
            await get_upload(user_id=current.user_id, upload_id=str(upload_id))
        )

    @router.put("/{upload_id}/parts/{index}", status_code=204)
    @inject
    async def part(
        upload_id: UUID,
        index: int,
        request: Request,
        content_length: int = Header(ge=0),
        x_content_sha256: str = Header(pattern="^[a-f0-9]{64}$"),
        current: SessionQueryModel = Depends(session),
        *,
        get_upload_part_size: FromDishka[GetUploadPartSizeInteractor],
        receive_upload_part: FromDishka[ReceiveUploadPartInteractor],
    ) -> None:
        expected = await get_upload_part_size(
            user_id=current.user_id, upload_id=str(upload_id), index=index
        )
        ensure(content_length == expected, InvalidRangeError, "Неверный размер части")
        data = bytearray()
        async for chunk in request.stream():
            ensure(
                len(data) + len(chunk) <= expected,
                PartTooLargeError,
                "Часть превышает размер",
            )
            data.extend(chunk)
        await receive_upload_part(
            user_id=current.user_id,
            upload_id=str(upload_id),
            index=index,
            data=data,
            expected_hash=x_content_sha256,
        )

    @router.post("/{upload_id}/complete")
    @inject
    async def complete(
        upload_id: UUID,
        response: Response,
        current: SessionQueryModel = Depends(session),
        *,
        complete_upload: FromDishka[CompleteUploadInteractor],
        get_upload: FromDishka[GetUploadInteractor],
    ) -> UploadResponse:
        await complete_upload(user_id=current.user_id, upload_id=str(upload_id))
        result = UploadResponse.from_upload(
            await get_upload(user_id=current.user_id, upload_id=str(upload_id))
        )
        response.status_code = 200 if result.state == "completed" else 202
        return result

    @router.delete("/{upload_id}", status_code=204)
    @inject
    async def cancel(
        upload_id: UUID,
        current: SessionQueryModel = Depends(session),
        *,
        cancel_upload: FromDishka[CancelUploadInteractor],
    ) -> None:
        await cancel_upload(user_id=current.user_id, upload_id=str(upload_id))

    return router
