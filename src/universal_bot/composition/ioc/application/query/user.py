from dishka import Provider, Scope, provide

from universal_bot.application.query.user.get_profile import GetProfileInteractor


class UserQueryProvider(Provider):
    scope = Scope.REQUEST
    get_profile_interactor = provide(GetProfileInteractor)
