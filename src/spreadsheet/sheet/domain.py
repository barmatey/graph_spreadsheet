from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellTable, CellValue
from src.node.domain import Node, Event
from src.spreadsheet.cell.domain import SheetCell


def size_factory():
    return 0, 0


class SheetNode(Node):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[SheetCell]] = Field(default_factory=list)

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

    def append_row(self, row: list[SheetCell]):
        if self.size[1] != 0 and self.size[1] != len(row):
            raise IndexError
        self.table.append(row)
        self.size = (self.size[0] + 1, len(row))
        self._events.append_event(RowAppended(sheet=self, row=row))


class SheetSubscriber(ABC):
    @abstractmethod
    def follow_sheet(self, sheet: SheetNode):
        raise NotImplemented


class RowAppended(Event):
    sheet: SheetNode
    row: list[SheetCell]
    uuid: UUID = Field(default_factory=uuid4)
