from dishka import Provider, Scope, provide

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.infrastructure.clock.system_clock import SystemClock
from universal_bot.infrastructure.security.secrets import SecureSecrets


class SecurityProvider(Provider):
    clock = provide(SystemClock, provides=IClock, scope=Scope.APP)
    secrets = provide(SecureSecrets, provides=ISecrets, scope=Scope.APP)
