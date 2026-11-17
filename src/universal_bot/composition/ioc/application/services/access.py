from dishka import Provider, Scope, provide

from universal_bot.application.service.access.access_policy import AccessPolicy


class AccessServicesProvider(Provider):
    scope = Scope.REQUEST
    access_policy = provide(AccessPolicy)
