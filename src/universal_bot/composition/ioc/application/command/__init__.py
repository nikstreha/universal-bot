from dishka import Provider

from universal_bot.composition.ioc.application.command.access import (
    AccessCommandProvider,
)
from universal_bot.composition.ioc.application.command.auth import AuthCommandProvider
from universal_bot.composition.ioc.application.command.file import FileCommandProvider
from universal_bot.composition.ioc.application.command.job import JobCommandProvider
from universal_bot.composition.ioc.application.command.telegram import (
    TelegramCommandProvider,
)
from universal_bot.composition.ioc.application.command.upload import (
    UploadCommandProvider,
)


def _command_provider() -> tuple[Provider, ...]:
    return (
        AccessCommandProvider(),
        AuthCommandProvider(),
        FileCommandProvider(),
        TelegramCommandProvider(),
        JobCommandProvider(),
        UploadCommandProvider(),
    )
