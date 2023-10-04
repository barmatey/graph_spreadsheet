from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellValue
from src.pubsub.domain import Pubsub, Event
from src.spreadsheet.sheet.domain import Sheet
from src.spreadsheet.sindex.domain import Sindex


class Cell(Pubsub):
    sheet: Sheet
    row_index: Sindex
    col_index: Sindex
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._events.append(CellCreated(entity=self))

    def __repr__(self):
        return f"Cell(index=({self.row_index.position}, {self.col_index.position}), value={self.value})"

    def __str__(self):
        return f"Cell(index=({self.row_index.position}, {self.col_index.position}), value={self.value})"

    def __eq__(self, other):
        return all([
            self.row_index.position == other.row_index.position,
            self.value == other.value,
            self.col_index.position == other.col_index.position,
        ])

    def __hash__(self) -> int:
        return self.uuid.__hash__()


CellTable = list[list[Cell]]


class CellCreated(Event):
    entity: Cell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
