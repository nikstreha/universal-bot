import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

from universal_bot.application.exception.common import FileTooLargeError
from universal_bot.application.exception.infrastructure.telegram import (
    BotNotConfiguredError,
)
from universal_bot.application.exception.transcription import (
    AudioTooLongError,
    AudioUnavailableError,
)
from universal_bot.application.port.transcription.recognizer import ISpeechRecognizer
from universal_bot.domain.common.guard import ensure


class FasterWhisperRecognizer(ISpeechRecognizer):
    def __init__(
        self,
        token: str,
        model: str,
        device: str,
        compute_type: str,
        directory: Path,
        max_seconds: int,
    ) -> None:
        self._token, self._model_name, self._device, self._compute = (
            token,
            model,
            device,
            compute_type,
        )
        self._directory, self._max_seconds, self._model = (directory, max_seconds, None)

    def _decode_audio(self, path: Path) -> NDArray[np.float32]:
        import numpy as np

        decoded = path.with_suffix(".f32")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-v",
                    "error",
                    "-y",
                    "-protocol_whitelist",
                    "file,pipe",
                    "-format_whitelist",
                    "aac,ac3,aiff,amr,ape,asf,au,avi,flac,matroska,webm,mov,mp3,mpeg,mpegts,ogg,wav,w64",
                    "-i",
                    str(path),
                    "-map",
                    "0:a:0",
                    "-vn",
                    "-sn",
                    "-dn",
                    "-t",
                    str(self._max_seconds + 1),
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-f",
                    "f32le",
                    "-acodec",
                    "pcm_f32le",
                    str(decoded),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=120,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise AudioUnavailableError("Не удалось прочитать аудиофайл") from exc
        samples = decoded.stat().st_size // 4
        ensure(samples > 0, AudioUnavailableError, "В файле нет аудиодорожки")
        ensure(
            samples <= self._max_seconds * 16000,
            AudioTooLongError,
            "Аудио слишком длинное",
        )
        return np.fromfile(decoded, dtype="<f4")

    def transcribe(self, telegram_file_id: str) -> str:
        ensure(self._token, BotNotConfiguredError, "Бот не настроен")
        self._directory.mkdir(parents=True, exist_ok=True)
        with (
            tempfile.TemporaryDirectory(dir=self._directory) as folder,
            httpx.Client(timeout=120) as client,
        ):
            result = client.post(
                f"https://api.telegram.org/bot{self._token}/getFile",
                json={"file_id": telegram_file_id},
            ).json()
            ensure(result.get("ok"), AudioUnavailableError, "Telegram не вернул файл")
            ensure(
                result["result"].get("file_size", 0) <= 20000000,
                FileTooLargeError,
                "Аудио больше 20 МБ",
            )
            path = Path(folder) / "audio"
            count = 0
            with (
                client.stream(
                    "GET",
                    f"https://api.telegram.org/file/bot{self._token}/{result['result']['file_path']}",
                ) as response,
                path.open("wb") as output,
            ):
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    count += len(chunk)
                    ensure(count <= 20000000, FileTooLargeError, "Аудио больше 20 МБ")
                    output.write(chunk)
            from faster_whisper import WhisperModel

            audio = self._decode_audio(path)
            if self._model is None:
                self._model = WhisperModel(
                    self._model_name, device=self._device, compute_type=self._compute
                )
            segments, info = self._model.transcribe(audio, beam_size=5, vad_filter=True)
            return "\n".join(
                segment.text.strip() for segment in segments if segment.text.strip()
            )
