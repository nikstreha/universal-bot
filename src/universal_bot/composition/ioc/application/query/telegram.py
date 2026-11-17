from dishka import Provider, Scope, provide

from universal_bot.application.query.telegram.get_access_request_status import (
    GetAccessRequestStatusInteractor,
)
from universal_bot.application.query.telegram.get_pending_telegram_updates import (
    GetPendingTelegramUpdatesInteractor,
)
from universal_bot.application.query.telegram.get_telegram_offset import (
    GetTelegramOffsetInteractor,
)


class TelegramQueryProvider(Provider):
    scope = Scope.REQUEST
    get_telegram_offset = provide(GetTelegramOffsetInteractor)
    get_pending_telegram_updates_interactor = provide(
        GetPendingTelegramUpdatesInteractor
    )
    get_access_request_status_interactor = provide(GetAccessRequestStatusInteractor)
