from dishka import Provider, Scope, provide

from universal_bot.application.query.access.get_access_request_list import (
    GetAccessRequestListInteractor,
)
from universal_bot.application.query.access.get_login_notification_list import (
    GetLoginNotificationListInteractor,
)
from universal_bot.application.query.access.get_user_list import GetUserListInteractor


class AccessQueryProvider(Provider):
    scope = Scope.REQUEST
    get_user_list_interactor = provide(GetUserListInteractor)
    get_access_request_list_interactor = provide(GetAccessRequestListInteractor)
    get_login_notification_list_interactor = provide(GetLoginNotificationListInteractor)
