from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command
from src.report.wire import domain as wire_domain
from src.spreadsheet.sheet import domain as sheet_domain


class PeriodNode(Node):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PeriodNode(from_date={self.from_date}, to_date={self.to_date})"

    @property
    def value(self):
        return self.to_date

    def is_filtred(self, wire: wire_domain.WireNode) -> bool:
        return self.from_date < wire.date <= self.to_date

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, sheet_domain.SheetNode):
                pass
            else:
                raise TypeError(f"invalid type: {type(pub)}")
        self._on_subscribed(pubs)

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented


class CreatePeriodNode(Command):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(default_factory=uuid4)
