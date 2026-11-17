from universal_bot.application.exception.common import UploadExpiredError
from universal_bot.application.query.upload.get_upload import GetUploadInteractor
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidRangeError, InvalidStateError


class GetUploadPartSizeInteractor:
    def __init__(self, *, get_upload: GetUploadInteractor) -> None:
        self._get_upload = get_upload

    async def __call__(self, *, user_id: int, upload_id: str, index: int) -> int:
        row, _ = await self._get_upload(user_id=user_id, upload_id=upload_id)
        ensure(row.state != "expired", UploadExpiredError, "Срок загрузки истёк")
        ensure(
            row.state == "receiving", InvalidStateError, "Загрузка не принимает части"
        )
        ensure(0 <= index < row.part_count, InvalidRangeError, "Неверный номер части")
        return min(row.part_bytes, row.size_bytes - index * row.part_bytes)
