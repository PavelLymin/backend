from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    __abstract__ = True

    def add_domain_event(self, event) -> None:
        if not hasattr(self, "_domain_events"):
            self._domain_events = []
        self._domain_events.append(event)

    def pull_domain_events(self) -> list:
        if not hasattr(self, "_domain_events"):
            return []
        events = self._domain_events[:]
        self._domain_events.clear()
        return events
