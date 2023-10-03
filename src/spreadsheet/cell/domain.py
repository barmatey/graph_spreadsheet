from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellValue
from src.core.pydantic_model import Model
from src.pubsub.domain import Pubsub, PubsubUpdated, Event
from src.spreadsheet.sindex.domain import Sindex


class Cell(Model):
    row_index: Sindex
    col_index: Sindex
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return f"Cell(index=({self.row_index.position}, {self.col_index.position}), value={self.value})"

    def __str__(self):
        return f"Cell(index=({self.row_index.position}, {self.col_index.position}), value={self.value})"

    def __eq__(self, other):
        return self.index == other.index and self.value == other.value

    def __hash__(self) -> int:
        return self.uuid.__hash__()


CellTable = list[list[Cell]]


class CellSubscriber(ABC):
    @abstractmethod
    def follow_cell_publishers(self, pubs: set[Cell]):
        raise NotImplemented

    @abstractmethod
    def on_cell_updated(self, old_value: Cell, new_value: Cell):
        raise NotImplemented

    @abstractmethod
    def on_cell_deleted(self, pub: Cell):
        raise NotImplemented


class CellTableSubscriber(ABC):
    @abstractmethod
    def follow_cell_table_publishers(self, pubs: set[CellTable]):
        raise NotImplemented

    @abstractmethod
    def on_cell_table_updated(self, old_table: CellTable, new_table: CellTable):
        raise NotImplemented


class SheetCell(Cell, Pubsub, CellSubscriber, CellTableSubscriber):
    def __init__(self, **data: Any):
        super().__init__(**data)
        self._events.append(CellCreated(entity=self))

    def on_cell_deleted(self, pub: Cell):
        raise NotImplemented

    def get_cell(self) -> Cell:
        return self

    def follow_cell_publishers(self, pubs: set[Cell]):
        old_value = self.model_copy(deep=True)
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            self.value = pub.get_cell().value
        self._on_followed(pubs)
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def follow_cell_table_publishers(self, pubs: set[CellTable]):
        old_value = self.model_copy(deep=True)
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            self.value = pub[self.index[0]][self.index[1]].value
        self._on_followed(pubs)
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_cell_updated(self, _old_value: Cell, new_value: Cell):
        old_value = self.model_copy(deep=True)
        self.value = new_value.value
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_cell_table_updated(self, _old_table: CellTable, new_table: CellTable):
        old_value = self.model_copy(deep=True)
        self.value = new_table[self.index[0]][self.index[1]].value
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def delete(self):
        self._events.append(CellDeleted(entity=self))


class CellCreated(Event):
    entity: SheetCell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class CellDeleted(Event):
    entity: SheetCell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 30


class CellUpdated(PubsubUpdated):
    old_value: SheetCell
    new_value: SheetCell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
