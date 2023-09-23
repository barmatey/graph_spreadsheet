from uuid import UUID

from src.helpers.decorators import singleton
from .domain import Node


class Base:
    def __init__(self):
        self._node_data = {}
        self._children_data = {}
        self._parent_data = {}


class NodeRepoFake(Base):
    def add(self, node: Node):
        if self._node_data.get(node.uuid) is not None:
            raise Exception
        self._node_data[node.uuid] = node

    def update(self, node: Node):
        if self._node_data.get(node.uuid) is None:
            raise LookupError
        self._node_data[node.uuid] = node

    def get_by_id(self, uuid: UUID) -> Node:
        return self._node_data[uuid]


class ChildrenRepoFake(Base):
    def get_node_children(self, uuid: UUID) -> set[UUID]:
        return self._children_data[uuid]

    def append_node_children(self, uuid: UUID, children: set[UUID]):
        if self._children_data.get(uuid) is None:
            self._children_data[uuid] = set()
        self._children_data[uuid] = self._children_data[uuid].union(children)


class ParentRepoFake(Base):
    def get_node_parents(self, uuid: UUID) -> set[UUID]:
        return self._parent_data[uuid]

    def append_node_parents(self, uuid: UUID, parents: set[UUID]):
        if self._parent_data.get(uuid) is None:
            self._parent_data[uuid] = set()
        self._parent_data[uuid] = self._parent_data[uuid].union(parents)


@singleton
class GraphRepoFake(NodeRepoFake, ParentRepoFake, ChildrenRepoFake):
    def add(self, node: Node):
        super().add(node)
        self.append_node_parents(node, set())
        self.append_node_children(node, set())

    def append_node_parents(self, node: Node, parents: set[Node]):
        node = node.uuid
        parents = set(x.uuid for x in parents)
        super().append_node_parents(node, parents)

    def append_node_children(self, node: Node, children: set[Node]):
        node = node.uuid
        children = set(x.uuid for x in children)
        super().append_node_children(node, children)

    def get_node_children(self, uuid: UUID) -> set[Node]:
        ids = super().get_node_children(uuid)
        nodes = set(self.get_by_id(x) for x in ids)
        return nodes

    def get_node_parents(self, uuid: UUID) -> set[Node]:
        ids = super().get_node_parents(uuid)
        nodes = set(self.get_by_id(x) for x in ids)
        return nodes
