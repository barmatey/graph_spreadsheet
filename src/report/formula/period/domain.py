from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command
from src.report.wire import domain as wire_domain


class PeriodNode(Node):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PeriodNode(from_date={self.from_date}, to_date={self.to_date})"

    def is_filtred(self, wire: wire_domain.WireNode) -> bool:
        return self.from_date < wire.date <= self.to_date


class PeriodSubscriber(ABC):
    @abstractmethod
    def follow_periods(self, pubs: set[PeriodNode]):
        raise NotImplemented

    @abstractmethod
    def on_period_updated(self, old_value: PeriodNode, new_value: PeriodNode):
        raise NotImplemented


class CreatePeriodNode(Command):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)
