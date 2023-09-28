from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellValue, CellTable
from src.node.domain import Node, Event, NodeUpdated


class CellValuePublisher(ABC):
    @abstractmethod
    def get_cell_value(self) -> CellValue:
        raise NotImplemented


class CellTablePublisher(Node, ABC):
    @abstractmethod
    def get_cell_table(self) -> CellTable:
        raise NotImplemented


class CellSubscriber(ABC):
    @abstractmethod
    def follow_cell_value_publisher(self, pub: CellValuePublisher):
        raise NotImplemented

    @abstractmethod
    def follow_cell_table_publisher(self, pub: CellTablePublisher):
        raise NotImplemented

    @abstractmethod
    def on_updated_value(self, old_value: CellValue, new_value: CellValue):
        raise NotImplemented

    @abstractmethod
    def on_updated_table(self, old_table: CellTable, new_table: CellTable):
        raise NotImplemented


class Cell(Node, CellSubscriber, CellValuePublisher):
    index: tuple[int, int]
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def __str__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def get_cell_value(self) -> CellValue:
        return self.value

    def follow_cell_value_publisher(self, pub: CellValuePublisher):
        self.value = pub.get_cell_value()
        self._on_subscribed({pub})
        logger.warning("Have to update!")

    def follow_cell_table_publisher(self, pub: CellTablePublisher):
        self.value = pub.get_cell_table()[self.index[0]][self.index[1]]
        self._on_subscribed({pub})
        logger.warning("Have to update!")

    def on_updated_value(self, old_value: CellValue, new_value: CellValue):
        self.value = new_value
        logger.warning("Have to update!")

    def on_updated_table(self, old_table: CellTable, new_table: CellTable):
        self.value = new_table[self.index[0]][self.index[1]]
        logger.warning("Have to update")



class CellUpdated(NodeUpdated):
    pass
