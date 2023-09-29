from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Pubsub, Command, PubsubUpdated
from src.report.wire import domain as wire_domain
from src.report.wire.domain import Ccol
from src.spreadsheet.cell.domain import Cell


class MapperNode(Pubsub):
    ccols: list[Ccol]
    filter_by: dict = Field(default_factory=dict)
    uuid: UUID = Field(default_factory=uuid4)

    def __str__(self):
        return f"MapperNode(filter_by={self.filter_by})"

    def is_filtred(self, wire: wire_domain.Wire) -> bool:
        return all([wire.__getattribute__(key) == value for key, value in self.filter_by.items()])

    def get_as_simple_row(self):
        return [self.filter_by[ccol] for ccol in self.ccols]

    def follow_cell_publishers(self, pubs: set[Cell]):
        old_value = self.model_copy(deep=True)
        for pub in pubs:
            key = self.ccols[pub.get_cell().index[1]]
            value = pub.get_cell().value
            self.filter_by[key] = value
        self._on_subscribed(pubs)
        self._on_updated(MapperUpdated(old_value=old_value, new_value=self))

    def on_updated_cell(self, old_value: Cell, new_value: Cell):
        old_value = self.model_copy(deep=True)
        key = self.ccols[new_value.index[1]]
        value = new_value.value
        self.filter_by[key] = value
        self._on_updated(MapperUpdated(old_value=old_value, new_value=self))


class MapperSubscriber(ABC):
    @abstractmethod
    def follow_mappers(self, pubs: set[MapperNode]):
        raise NotImplemented

    @abstractmethod
    def on_mapper_update(self, old_value: MapperNode, new_value: MapperNode):
        raise NotImplemented


class MapperUpdated(PubsubUpdated):
    old_value: MapperNode
    new_value: MapperNode
    uuid: UUID = Field(default_factory=uuid4)
