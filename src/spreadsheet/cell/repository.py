from abc import ABC, abstractmethod
from uuid import UUID

from src.pubsub.repository import GraphRepoFake
from .domain import SheetCell


class CellRepo(ABC):
    @abstractmethod
    def get_one_by_id(self, uuid: UUID) -> SheetCell:
        raise NotImplemented

    @abstractmethod
    def get_many(self, filter_by: dict, order_by: list, asc: bool = True) -> list[SheetCell]:
        raise NotImplemented


class CellRepoFake(CellRepo):
    def __init__(self):
        self._grepo = GraphRepoFake()

    def get_one_by_id(self, uuid: UUID) -> SheetCell:
        node = self._grepo.get_by_id(uuid)
        if not isinstance(node, SheetCell):
            raise Exception
        return node

    def get_many(self, filter_by: dict, order_by: list, asc: bool = True) -> list[SheetCell]:
        all_nodes = self._grepo._node_data.values()
        result: list[SheetCell] = []
        for node in all_nodes:
            if all([node.__getattribute__(key) == value for key, value in filter_by.items()]):
                if isinstance(node, SheetCell):
                    result.append(node)
        result = sorted(result)
        return result
