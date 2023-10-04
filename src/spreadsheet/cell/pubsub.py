from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event, PubsubUpdated
from src.spreadsheet.cell.domain import Cell, CellTable


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


class CellPublisher(Cell, CellSubscriber, CellTableSubscriber):

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


class CellDeleted(Event):
    entity: Cell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class CellUpdated(PubsubUpdated):
    old_value: Cell
    new_value: Cell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
