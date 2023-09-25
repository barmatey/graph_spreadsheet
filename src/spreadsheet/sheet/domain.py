from uuid import UUID, uuid4

from pydantic import Field


from src.node.domain import Command, Node, Event
from src.report.wire.domain import Ccol


class SheetNode(Node):
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented


class CreateGroupSheetNode(Command):
    title: str
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)
