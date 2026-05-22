from dishka import Provider, Scope, provide

from application.protocols.clock import Clock
from infrastructure.clock import SystemClock


class DomainProvider(Provider):

    scope = Scope.APP

    clock = provide(source=SystemClock, provides=Clock)
