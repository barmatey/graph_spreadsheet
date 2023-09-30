from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable, CellValue
from src.pubsub.domain import Pubsub, Event
from src.spreadsheet.cell.domain import SheetCell
from src.spreadsheet.sindex.handlers import Sindex


def size_factory():
    return 0, 0


class Sheet(Pubsub):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[SheetCell]] = Field(default_factory=list)
    rows: list[Sindex] = Field(default_factory=list)
    cols: list[Sindex] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)
    _reindexed: bool = False

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

    def append_rows(self, rows: Sindex | list[Sindex], cells: list[SheetCell] | list[list[SheetCell]]):
        if len(cells) and isinstance(cells[0], SheetCell):
            cells = [cells]
        if isinstance(rows, Sindex):
            rows = [rows]
        if len(rows) != len(cells):
            raise Exception(f'len rows != len cells, {len(rows)} != {len(cells)}')

        for sindex, values in zip(rows, cells):
            if self.size[1] != 0 and self.size[1] != len(values):
                raise Exception(f"self.size[1] != len(values), {self.size[1]} != {len(values)}")
            self.table.append(values)
            self.rows.append(sindex)
            self.size = (self.size[0] + 1, len(values))
        self._events.append(RowsAppended(sheet=self, rows=rows, cells=cells))

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
        self._events.append(RowsDeleted(sheet=self, rows=deleted_rows))

    def reindex(self):
        for i in range(0, self.size[0]):
            for j in range(0, self.size[1]):
                self.table[i][j].row_index.position = i
                self.table[i][j].col_index.position = j
        self._reindexed = True

    def parse_events(self) -> list[Event]:
        events = super().parse_events()
        if self._reindexed:
            events.append(RowsReindexed(sheet=self))
            self._reindexed = False
        return events


class SheetSubscriber(ABC):
    @abstractmethod
    def follow_sheet(self, sheet: Sheet):
        raise NotImplemented

    @abstractmethod
    def on_rows_appended(self, rows: list[Sindex], cells: list[list[SheetCell]]):
        raise NotImplemented


class RowsAppended(Event):
    sheet: Sheet
    cells: list[list[SheetCell]]
    rows: list[Sindex]
    uuid: UUID = Field(default_factory=uuid4)


class RowsDeleted(Event):
    sheet: Sheet
    rows: list[list[SheetCell]]
    uuid: UUID = Field(default_factory=uuid4)


class RowsReindexed(Event):
    sheet: Sheet
    uuid: UUID = Field(default_factory=uuid4)
