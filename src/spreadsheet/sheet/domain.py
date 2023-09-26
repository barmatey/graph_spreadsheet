from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable
from src.node.domain import Node, Event
from src.spreadsheet.cell.domain import CellNode


class SheetNode(Node):
    size: tuple[int, int] = Field(default_factory=tuple)
    table: list[list[CellNode]] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def __str__(self):
        return f"{self.__class__.__name__}(size={self.size})"

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented
