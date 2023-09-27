from loguru import logger
from pydantic import Field

from src.core.cell import CellTable, CellValue
from src.node.domain import Node, Event
from src.spreadsheet.cell.domain import CellNode


def size_factory():
    return 0, 0


class SheetNode(Node):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[CellNode]] = Field(default_factory=list)

    def __str__(self):
        return f"{self.__class__.__name__}(size={self.size})"

    def get_as_simple_table(self) -> CellTable:
        result: CellTable = []
        for row in self.table:
            r: list[CellValue] = []
            for cell in row:
                r.append(cell.value)
            result.append(r)
        return result

    def append_row(self, row: list[CellNode]):
        if self.size[1] != 0 and self.size[1] != len(row):
            raise IndexError
        self.table.append(row)
        self.size = (self.size[0] + 1, len(row))
        logger.warning("row was appended, but not notified")

    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented
