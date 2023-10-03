from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable, CellValue
from src.pubsub.domain import Pubsub, Event
from src.spreadsheet.cell.domain import SheetCell, CellDeleted
from src.spreadsheet.sindex.domain import Sindex, SindexDeleted


def size_factory():
    return 0, 0


class Sheet(Pubsub):
    size: tuple[int, int] = Field(default_factory=size_factory)
    table: list[list[SheetCell]] = Field(default_factory=list)
    rows: list[Sindex] = Field(default_factory=list)
    cols: list[Sindex] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SheetCreated(entity=self))

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

        if self.size[1] == 0:
            self.cols = [x.col_index for x in cells[0]]
            self.size = (self.size[0], len(self.cols))

        for sindex, values in zip(rows, cells):
            if self.size[1] != len(values):
                raise Exception(f"self.size[1] != len(values), {self.size[1]} != {len(values)}")
            self.table.append(values)
            self.rows.append(sindex)
            self.size = (self.size[0] + 1, len(values))
        self._events.append(RowsAppended(sheet=self, rows=rows, cells=cells))

    def delete_rows(self, indexes: list[int]):
        hashes = {index: 1 for index in indexes}
        new_table = []
        new_rows = []
        deleted_rows = []
        deleted_cells = []
        for i, row in enumerate(self.table):
            if hashes.get(i) is None:
                new_table.append(self.table[i])
                new_rows.append(self.rows[i])
            else:
                deleted_rows.append(self.rows[i])
                self._events.append(SindexDeleted(entity=self.rows[i]))
                for cell in self.table[i]:
                    deleted_cells.append(cell)

        self.table = new_table
        self.rows = new_rows
        self.size = (len(new_table), self.size[1] if len(new_table) else 0)
        self.reindex()

    def reindex(self):
        for i in range(0, self.size[0]):
            self.rows[i].position = i
        for j in range(0, self.size[1]):
            self.cols[j].position = j
        self._events.append(SheetReindexed(sheet=self), unique=True, unique_key=f"{self.uuid}")


class SheetSubscriber(ABC):
    @abstractmethod
    def follow_sheet(self, sheet: Sheet):
        raise NotImplemented

    @abstractmethod
    def on_rows_appended(self, rows: list[Sindex], cells: list[list[SheetCell]]):
        raise NotImplemented


class SheetCreated(Event):
    entity: Sheet
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class RowsAppended(Event):
    sheet: Sheet
    cells: list[list[SheetCell]]
    rows: list[Sindex]
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class RowsDeleted(Event):
    sheet: Sheet
    deleted_rows: list[Sindex]
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class SheetReindexed(Event):
    sheet: Sheet
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 30
