from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command
from src.report.wire import domain as wire_domain


class PeriodNode(Node):
    from_date: datetime
    to_date: datetime
    events: list = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PeriodNode(from_date={self.from_date}, to_date={self.to_date})"

    def is_filtred(self, wire: wire_domain.WireNode) -> bool:
        return self.from_date < wire.date <= self.to_date

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented


class CreatePeriodNode(Command):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)
