from dishka import Provider, Scope, provide

from universal_bot.application.query.auth.get_denied_login_identity import (
    GetDeniedLoginIdentityInteractor,
)
from universal_bot.application.query.auth.get_session_list import (
    GetSessionListInteractor,
)


class AuthQueryProvider(Provider):
    scope = Scope.REQUEST
    get_denied_login_identity_interactor = provide(GetDeniedLoginIdentityInteractor)
    get_session_list_interactor = provide(GetSessionListInteractor)
