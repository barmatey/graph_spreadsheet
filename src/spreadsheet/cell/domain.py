from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellValue
from src.core.pydantic_model import Model
from src.pubsub.domain import Pubsub, PubsubUpdated


class Cell(Model):
    index: tuple[int, int]
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def __str__(self):
        return f"Cell(index={self.index}, value={self.value})"

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
    def on_updated_cell(self, old_value: Cell, new_value: Cell):
        raise NotImplemented


class CellTableSubscriber(ABC):
    @abstractmethod
    def follow_cell_table_publishers(self, pubs: set[CellTable]):
        raise NotImplemented

    @abstractmethod
    def on_updated_cell_table(self, old_table: CellTable, new_table: CellTable):
        raise NotImplemented


class SheetCell(Cell, Pubsub, CellSubscriber, CellTableSubscriber):
    def get_cell(self) -> Cell:
        return self

    def follow_cell_publishers(self, pubs: set[Cell]):
        old_value = self.model_copy(deep=True)
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            self.value = pub.get_cell().value
        self._on_subscribed(pubs)
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def follow_cell_table_publishers(self, pubs: set[CellTable]):
        old_value = self.model_copy(deep=True)
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            self.value = pub[self.index[0]][self.index[1]].value
        self._on_subscribed(pubs)
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_updated_cell(self, _old_value: Cell, new_value: Cell):
        old_value = self.model_copy(deep=True)
        self.value = new_value.value
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_updated_cell_table(self, _old_table: CellTable, new_table: CellTable):
        old_value = self.model_copy(deep=True)
        self.value = new_table[self.index[0]][self.index[1]].value
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))


class CellUpdated(PubsubUpdated):
    old_value: SheetCell
    new_value: SheetCell
    uuid: UUID = Field(default_factory=uuid4)
