import tempfile
from pathlib import Path

import httpx

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
            from faster_whisper.audio import decode_audio

            audio = decode_audio(str(path), sampling_rate=16000)
            ensure(
                len(audio) / 16000 <= self._max_seconds,
                AudioTooLongError,
                "Аудио слишком длинное",
            )
            if self._model is None:
                self._model = WhisperModel(
                    self._model_name, device=self._device, compute_type=self._compute
                )
            segments, info = self._model.transcribe(audio, beam_size=5, vad_filter=True)
            return "\n".join(
                segment.text.strip() for segment in segments if segment.text.strip()
            )
