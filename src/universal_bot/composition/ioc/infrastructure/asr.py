from dishka import Provider, Scope, provide

from universal_bot.application.port.transcription.recognizer import ISpeechRecognizer
from universal_bot.composition.configuration.asr_configuration import AsrConfiguration
from universal_bot.composition.configuration.telegram_configuration import (
    TelegramConfiguration,
)
from universal_bot.infrastructure.transcription.whisper import FasterWhisperRecognizer


class AsrProvider(Provider):
    @provide(scope=Scope.APP)
    def recognizer(
        self, config: AsrConfiguration, telegram: TelegramConfiguration
    ) -> ISpeechRecognizer:
        return FasterWhisperRecognizer(
            telegram.token,
            config.model,
            config.device,
            config.compute_type,
            config.temporary_directory,
            config.max_audio_seconds,
        )
