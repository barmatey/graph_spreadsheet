from abc import ABC, abstractmethod
from uuid import UUID, uuid4
from pydantic import Field

from src.core.cell import CellValue, CellTable
from src.node.domain import Node, Event


class CellValuePublisher(ABC):
    @abstractmethod
    def get_cell_value(self) -> CellValue:
        raise NotImplemented


class CellTablePublisher(ABC):
    @abstractmethod
    def get_cell_table(self) -> CellTable:
        raise NotImplemented


class CellSubscriber(ABC):
    @abstractmethod
    def on_updated_value(self, old_value: CellValue, new_value: CellValue):
        raise NotImplemented

    @abstractmethod
    def on_updated_table(self, old_table: CellTable, new_table: CellTable):
        raise NotImplemented


class Cell(Node):
    index: tuple[int, int]
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)

    def __repr__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def __str__(self):
        return f"Cell(index={self.index}, value={self.value})"

    def follow(self, pubs: set['Node']):
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            if not hasattr(pub, "value"):
                raise Exception
            if isinstance(pub.value, CellValue):
                self.value = pub.value
            elif isinstance(pub.value, list):
                self.value = pub.value[self.index[0]][self.index[1]]
            else:
                raise TypeError(f"real type is: {type(pub)}")
        self._on_subscribed(pubs)
        self._on_updated()

    def update(self, old_value: 'Node', new_value: 'Node'):
        if not hasattr(new_value, "value"):
            raise Exception
        if old_value.value == new_value.value:
            return

        if isinstance(new_value.value, CellValue):
            self.value = new_value.value
        elif isinstance(new_value.value, list):
            self.value = new_value.value[self.index[0]][self.index[1]]
        else:
            raise TypeError(f"real type is: {type(new_value)}")
        self._on_updated()

    def _on_updated(self):
        pass
