from dishka import Provider

from universal_bot.composition.ioc.infrastructure.asr import AsrProvider
from universal_bot.composition.ioc.infrastructure.file_storage import (
    FileStorageProvider,
)
from universal_bot.composition.ioc.infrastructure.media import MediaProvider
from universal_bot.composition.ioc.infrastructure.messaging import MessagingProvider
from universal_bot.composition.ioc.infrastructure.persistence import (
    PersistenceProvider,
)
from universal_bot.composition.ioc.infrastructure.security import SecurityProvider


def _infrastructure_provider() -> tuple[Provider, ...]:
    return (
        PersistenceProvider(),
        FileStorageProvider(),
        MediaProvider(),
        SecurityProvider(),
        AsrProvider(),
        MessagingProvider(),
    )
