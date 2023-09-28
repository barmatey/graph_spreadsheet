from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable, CellValue
from src.node.domain import Node, Event
from src.spreadsheet.cell.domain import SheetCell


def size_factory():
    return 0, 0


class Sheet(Node):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[SheetCell]] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

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

    def append_rows(self, rows: list[SheetCell] | list[list[SheetCell]]):
        if len(rows) and isinstance(rows[0], SheetCell):
            rows = [rows]
        for row in rows:
            if self.size[1] != 0 and self.size[1] != len(row):
                raise IndexError
            self.table.append(row)
            self.size = (self.size[0] + 1, len(row))
        self._events.append_event(RowsAppended(sheet=self, rows=rows))

    def delete_rows(self, indexes: list[int]):
        hashes = {index: 1 for index in indexes}
        deleted_rows = []
        new_table = []
        for i, row in enumerate(self.table):
            if hashes.get(i) is None:
                new_table.append(self.table[i])
            else:
                deleted_rows.append(self.table[i])
        self.table = new_table
        self.size = (len(new_table), self.size[1] if len(new_table) else 0)
        self.reindex()
        self._events.append_event(RowsDeleted(sheet=self, rows=deleted_rows))

    def reindex(self):
        for i in range(0, self.size[0]):
            for j in range(0, self.size[1]):
                self.table[i][j].index = (i, j)


class SheetSubscriber(ABC):
    @abstractmethod
    def follow_sheet(self, sheet: Sheet):
        raise NotImplemented


class RowsAppended(Event):
    sheet: Sheet
    rows: list[list[SheetCell]]
    uuid: UUID = Field(default_factory=uuid4)


class RowsDeleted(Event):
    sheet: Sheet
    rows: list[list[SheetCell]]
    uuid: UUID = Field(default_factory=uuid4)
