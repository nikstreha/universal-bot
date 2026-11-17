from dishka import Provider

from universal_bot.composition.ioc.application.query.access import AccessQueryProvider
from universal_bot.composition.ioc.application.query.auth import AuthQueryProvider
from universal_bot.composition.ioc.application.query.file import FileQueryProvider
from universal_bot.composition.ioc.application.query.telegram import (
    TelegramQueryProvider,
)
from universal_bot.composition.ioc.application.query.upload import UploadQueryProvider
from universal_bot.composition.ioc.application.query.user import UserQueryProvider


def _query_provider() -> tuple[Provider, ...]:
    return (
        AccessQueryProvider(),
        AuthQueryProvider(),
        FileQueryProvider(),
        TelegramQueryProvider(),
        UploadQueryProvider(),
        UserQueryProvider(),
    )
