from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellTable
from src.node.domain import Node, Event
from src.spreadsheet.cell.domain import CellNode


def size_factory():
    return 0, 0


class SheetNode(Node):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[CellNode]] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def __str__(self):
        return f"{self.__class__.__name__}(size={self.size})"

    def append_row(self, row: list[CellNode]):
        if self.size[1] != 0 and self.size[1] != len(row):
            raise IndexError
        self.table.append(row)
        logger.warning("row was appended, but not notified")

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented
