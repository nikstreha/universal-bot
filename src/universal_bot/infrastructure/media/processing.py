import io
import subprocess
import tempfile
import warnings
from pathlib import Path

import filetype
from PIL import Image, ImageOps

from universal_bot.application.exception.common import (
    ThumbnailTooLargeError,
    UnsupportedPreviewError,
)
from universal_bot.application.port.media.inspector import IMediaInspector
from universal_bot.application.port.media.thumbnailer import IThumbnailer
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.domain.common.guard import ensure


class FiletypeInspector(IMediaInspector):
    def classify(self, header: bytes) -> tuple[str, str]:
        kind = filetype.guess(header)
        mime = kind.mime if kind else "application/octet-stream"
        category = (
            "photo"
            if mime.startswith("image/")
            else "video"
            if mime.startswith("video/")
            else "audio"
            if mime.startswith("audio/")
            else "other"
        )
        return (category, mime)


class LocalThumbnailer(IThumbnailer):
    def __init__(self, storage: IObjectStorage, temporary_directory: Path) -> None:
        self._storage, self._directory = (storage, temporary_directory)

    def create(
        self, object_key: str, target_key: str, media_kind: str, size_bytes: int
    ) -> None:
        ensure(
            size_bytes <= 1024**3,
            ThumbnailTooLargeError,
            "Оригинал слишком велик для предпросмотра",
        )
        self._directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=self._directory) as folder:
            path = Path(folder) / "source"
            self._storage.download(object_key, str(path))
            if media_kind == "video":
                output = Path(folder) / "frame.jpg"
                with path.open("rb") as stream:
                    detected = filetype.guess(stream.read(8192))
                demuxer = {
                    "video/mp4": "mov",
                    "video/quicktime": "mov",
                    "video/webm": "matroska",
                    "video/x-matroska": "matroska",
                    "video/x-msvideo": "avi",
                    "video/mpeg": "mpeg",
                    "video/ogg": "ogg",
                }.get(detected.mime if detected else "")
                ensure(
                    demuxer,
                    UnsupportedPreviewError,
                    "Предпросмотр этого контейнера не поддерживается",
                )
                subprocess.run(
                    [
                        "ffmpeg",
                        "-nostdin",
                        "-v",
                        "error",
                        "-protocol_whitelist",
                        "file",
                        "-f",
                        demuxer,
                        *(["-enable_drefs", "0"] if demuxer == "mov" else []),
                        "-ss",
                        "0",
                        "-i",
                        str(path),
                        "-frames:v",
                        "1",
                        "-vf",
                        "scale=640:-2",
                        "-y",
                        str(output),
                    ],
                    check=True,
                    timeout=120,
                    capture_output=True,
                )
                path = output
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(path) as dimensions:
                    ensure(
                        dimensions.width * dimensions.height <= 40000000,
                        ThumbnailTooLargeError,
                        "Слишком большое разрешение изображения",
                    )
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((640, 640))
                data = io.BytesIO()
                image.save(data, "JPEG", quality=82)
            self._storage.put(target_key, data.getvalue(), "image/jpeg")
