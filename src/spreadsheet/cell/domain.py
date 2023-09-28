from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellValue
from src.core.pydantic_model import Model
from src.node.domain import Node, NodeUpdated


class Cell(Model):
    index: tuple[int, int]
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def __str__(self):
        return f"Cell(index={self.index}, value={self.value})"


CellTable = list[list[CellValue]]


class CellPublisher(ABC):
    @abstractmethod
    def get_cell(self) -> Cell:
        raise NotImplemented


class CellTablePublisher(ABC):
    @abstractmethod
    def get_cell_table(self) -> CellTable:
        raise NotImplemented


class CellSubscriber(ABC):
    @abstractmethod
    def follow_cell_publisher(self, pub: CellPublisher):
        raise NotImplemented

    @abstractmethod
    def on_updated_cell(self, old_value: Cell, new_value: Cell):
        raise NotImplemented


class CellTableSubscriber(ABC):
    @abstractmethod
    def follow_cell_table_publisher(self, pub: CellTablePublisher):
        raise NotImplemented

    @abstractmethod
    def on_updated_cell_table(self, old_table: CellTable, new_table: CellTable):
        raise NotImplemented


class SheetCell(Cell, Node, CellSubscriber, CellTableSubscriber, CellPublisher):
    def get_cell(self) -> Cell:
        return self

    def follow_cell_publisher(self, pub: CellPublisher):
        self.value = pub.get_cell().value
        self._on_subscribed({pub})
        logger.warning("Have to update!")

    def follow_cell_table_publisher(self, pub: CellTablePublisher):
        self.value = pub.get_cell_table()[self.index[0]][self.index[1]].value
        self._on_subscribed({pub})
        logger.warning("Have to update!")

    def on_updated_cell(self, old_value: Cell, new_value: Cell):
        self.value = new_value.value
        logger.warning("Have to update!")

    def on_updated_cell_table(self, old_table: CellTable, new_table: CellTable):
        self.value = new_table[self.index[0]][self.index[1]].value
        logger.warning("Have to update")


class CellUpdated(NodeUpdated):
    pass
