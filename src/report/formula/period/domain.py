from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Pubsub, Event
from src.report.wire import domain as wire_domain


class Period(Pubsub):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(PeriodCreated(entity=self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PeriodNode(from_date={self.from_date}, to_date={self.to_date})"

    def is_filtred(self, wire: wire_domain.Wire) -> bool:
        return self.from_date < wire.date <= self.to_date


class PeriodSubscriber(ABC):
    @abstractmethod
    def follow_periods(self, pubs: set[Period]):
        raise NotImplemented

    @abstractmethod
    def on_period_updated(self, old_value: Period, new_value: Period):
        raise NotImplemented


class PeriodCreated(Event):
    entity: Period
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
