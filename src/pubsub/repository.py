from uuid import UUID

import loguru

from src.helpers.decorators import singleton
from .domain import Pubsub


class Base:
    def __init__(self):
        self._node_data: dict[UUID, Pubsub] = {}
        self._children_data = {}
        self._parent_data = {}


class NodeRepoFake(Base):
    def add(self, node: Pubsub):
        if self._node_data.get(node.uuid) is not None:
            raise Exception(f"already exist: {type(node)}")
        self._node_data[node.uuid] = node

    def remove(self, pub: Pubsub):
        if self._node_data.get(pub.uuid) is None:
            raise Exception
        del self._node_data[pub.uuid]

    def update(self, node: Pubsub):
        if self._node_data.get(node.uuid) is None:
            raise LookupError(f"node: {node}")
        self._node_data[node.uuid] = node

    def get_by_id(self, uuid: UUID) -> Pubsub:
        return self._node_data[uuid]



class ChildrenRepoFake(Base):
    def get_node_children(self, uuid: UUID) -> set[UUID]:
        return self._children_data[uuid]

    def append_node_children(self, uuid: UUID, children: set[UUID]):
        if self._children_data.get(uuid) is None:
            self._children_data[uuid] = set()
        self._children_data[uuid] = self._children_data[uuid].union(children)

    def remove_node_children(self, uuid: UUID):
        if self._children_data.get(uuid) is None:
            raise Exception
        del self._children_data[uuid]


class ParentRepoFake(Base):
    def get_node_parents(self, uuid: UUID) -> set[UUID]:
        return self._parent_data[uuid]

    def append_node_parents(self, uuid: UUID, parents: set[UUID]):
        if self._parent_data.get(uuid) is None:
            self._parent_data[uuid] = set()
        self._parent_data[uuid] = self._parent_data[uuid].union(parents)

    def remove_node_parents(self, uuid: UUID):
        if self._parent_data.get(uuid) is None:
            raise Exception
        del self._parent_data[uuid]


class GraphRepo(NodeRepoFake, ParentRepoFake, ChildrenRepoFake):
    pass


@singleton
class GraphRepoFake(GraphRepo):
    def add(self, node: Pubsub):
        super().add(node)
        self.append_node_parents(node, set())
        self.append_node_children(node, set())

    def remove(self, pub: Pubsub):
        super().remove(pub)
        for child in super().get_node_children(pub.uuid):
            self._parent_data[child].remove(pub.uuid)
        for parent in super().get_node_parents(pub.uuid):
            self._children_data[parent].remove(pub.uuid)
        self.remove_node_children(pub.uuid)
        self.remove_node_parents(pub.uuid)

    def append_node_parents(self, node: Pubsub, parents: set[Pubsub]):
        node = node.uuid
        parents = set(x.uuid for x in parents)
        super().append_node_parents(node, parents)

    def append_node_children(self, node: Pubsub, children: set[Pubsub]):
        node = node.uuid
        children = set(x.uuid for x in children)
        super().append_node_children(node, children)

    def get_node_children(self, node: Pubsub) -> set[Pubsub]:
        ids = super().get_node_children(node.uuid)
        nodes = set(self.get_by_id(x) for x in ids)
        return nodes

    def get_node_parents(self, node: Pubsub) -> set[Pubsub]:
        ids = super().get_node_parents(node.uuid)
        nodes = set(self.get_by_id(x) for x in ids)
        return nodes
