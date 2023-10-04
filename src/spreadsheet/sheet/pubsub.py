from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event
from src.spreadsheet.cell.domain import Cell
from src.spreadsheet.sheet.domain import Sheet
from src.spreadsheet.sindex.domain import Sindex


class SheetPublisher(Sheet):
    pass


class SheetSubscriber(ABC):
    @abstractmethod
    def follow_sheet(self, sheet: Sheet):
        raise NotImplemented

    @abstractmethod
    def on_rows_appended(self, rows: list[Sindex], cells: list[list[Cell]]):
        raise NotImplemented

    @abstractmethod
    def on_rows_deleted(self, rows: list[Sindex]):
        raise NotImplemented


class RowsAppended(Event):
    sheet: Sheet
    cells: list[list[Cell]]
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
