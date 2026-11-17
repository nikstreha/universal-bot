import asyncio
import re
from urllib.parse import quote

from starlette.responses import StreamingResponse

from universal_bot.application.command.auth.authenticate_session import (
    AuthenticateSessionInteractor,
)
from universal_bot.application.exception.common import (
    RangeNotSatisfiableError,
    ThumbnailNotReadyError,
)
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.query.file.get_file import GetFileInteractor
from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.file import FileTrashedError


class FileResponseFactory:
    def __init__(
        self,
        *,
        authenticate: AuthenticateSessionInteractor,
        get_file: GetFileInteractor,
        storage: IObjectStorage,
        clock: IClock,
    ) -> None:
        self._authenticate = authenticate
        self._get_file = get_file
        self._storage = storage
        self._clock = clock

    async def __call__(
        self,
        row: StoredFileQueryModel,
        authorization: str,
        range_header: str = "",
        inline: bool = False,
        thumbnail: bool = False,
    ) -> StreamingResponse:
        ensure(row.state == "active", FileTrashedError, "Сначала восстановите файл")
        key = row.thumbnail_key if thumbnail else row.object_key
        ensure(key, ThumbnailNotReadyError, "Миниатюра пока недоступна")
        size = await asyncio.to_thread(self._storage.size, key)
        start = 0
        end = size - 1
        partial = False
        if range_header:
            match = re.fullmatch("bytes=(\\d*)-(\\d*)", range_header)
            ensure(
                match and size > 0 and any(match.groups()),
                RangeNotSatisfiableError,
                "Неверный диапазон",
            )
            a, b = match.groups()
            start = int(a) if a else max(0, size - int(b))
            end = min(size - 1, int(b)) if a and b else size - 1
            ensure(
                0 <= start <= end < size, RangeNotSatisfiableError, "Диапазон вне файла"
            )
            partial = True
        length = max(0, end - start + 1)

        async def chunks():
            if not length:
                return
            source = await asyncio.to_thread(self._storage.read, key, start, length)
            checked = 0
            try:
                while chunk := (await asyncio.to_thread(source.read, 256 * 1024)):
                    if self._clock.now() - checked >= 2:
                        current = await self._authenticate(secret=authorization[7:])
                        ensure(
                            (
                                await self._get_file(
                                    user_id=current.user_id, file_id=row.id
                                )
                            ).state
                            == "active",
                            FileTrashedError,
                            "Передача остановлена",
                        )
                        checked = self._clock.now()
                    yield chunk
            finally:
                await asyncio.to_thread(self._storage.close, source)

        mime = "image/jpeg" if thumbnail else row.mime_type
        safe_inline = inline and (
            mime.startswith("image/")
            and mime != "image/svg+xml"
            or mime.startswith(("video/", "audio/"))
        )
        headers = {
            "Content-Length": str(length),
            "Accept-Ranges": "bytes",
            "ETag": '"' + row.sha256 + '"',
            "Content-Disposition": (
                "inline" if safe_inline or thumbnail else "attachment"
            )
            + "; filename*=UTF-8''"
            + quote(row.original_name, safe=""),
        }
        if partial:
            headers["Content-Range"] = f"bytes {start}-{end}/{size}"
        return StreamingResponse(
            chunks(),
            status_code=206 if partial else 200,
            media_type=mime,
            headers=headers,
        )
