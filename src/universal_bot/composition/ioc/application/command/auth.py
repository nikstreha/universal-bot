from dishka import Provider, Scope, provide

from universal_bot.application.command.auth.authenticate_session import (
    AuthenticateSessionInteractor,
)
from universal_bot.application.command.auth.bind_login_attempt import (
    BindLoginAttemptInteractor,
)
from universal_bot.application.command.auth.confirm_login_attempt import (
    ConfirmLoginAttemptInteractor,
)
from universal_bot.application.command.auth.create_login_attempt import (
    CreateLoginAttemptInteractor,
)
from universal_bot.application.command.auth.exchange_login_attempt import (
    ExchangeLoginAttemptInteractor,
)
from universal_bot.application.command.auth.revoke_session import (
    RevokeSessionInteractor,
)


class AuthCommandProvider(Provider):
    scope = Scope.REQUEST
    create_login_attempt_interactor = provide(CreateLoginAttemptInteractor)
    bind_login_attempt_interactor = provide(BindLoginAttemptInteractor)
    confirm_login_attempt_interactor = provide(ConfirmLoginAttemptInteractor)
    exchange_login_attempt_interactor = provide(ExchangeLoginAttemptInteractor)
    authenticate_session_interactor = provide(AuthenticateSessionInteractor)
    revoke_session_interactor = provide(RevokeSessionInteractor)
