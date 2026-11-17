from dishka import Provider, Scope, provide

from universal_bot.application.command.access.apply_rate_limit import (
    ApplyRateLimitInteractor,
)
from universal_bot.application.command.access.decide_access_request import (
    DecideAccessRequestInteractor,
)
from universal_bot.application.command.access.grant_access import GrantAccessInteractor
from universal_bot.application.command.access.initialize_service import (
    InitializeServiceInteractor,
)
from universal_bot.application.command.access.mark_login_notifications_read import (
    MarkLoginNotificationsReadInteractor,
)
from universal_bot.application.command.access.observe_telegram_user import (
    ObserveTelegramUserInteractor,
)
from universal_bot.application.command.access.request_access import (
    RequestAccessInteractor,
)
from universal_bot.application.command.access.revoke_access import (
    RevokeAccessInteractor,
)


class AccessCommandProvider(Provider):
    scope = Scope.REQUEST
    observe_telegram_user_interactor = provide(ObserveTelegramUserInteractor)
    grant_access_interactor = provide(GrantAccessInteractor)
    revoke_access_interactor = provide(RevokeAccessInteractor)
    request_access_interactor = provide(RequestAccessInteractor)
    decide_access_request_interactor = provide(DecideAccessRequestInteractor)
    mark_login_notifications_read_interactor = provide(
        MarkLoginNotificationsReadInteractor
    )
    apply_rate_limit_interactor = provide(ApplyRateLimitInteractor)

    initialize_service = provide(InitializeServiceInteractor)
