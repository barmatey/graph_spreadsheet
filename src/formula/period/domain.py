from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command


class PeriodNode(Node):
    from_date: datetime
    to_date: datetime
    events: list = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented


class CreatePeriodNode(Command):
    from_date: datetime
    to_date: datetime
    uuid: UUID = Field(uuid4)
