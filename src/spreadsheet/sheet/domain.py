from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable
from src.node.domain import Node, Event


class SheetNode(Node):
    events: list[Event] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented
