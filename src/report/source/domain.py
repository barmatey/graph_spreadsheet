from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Event, Command, NodeUpdated
from src.report.wire import domain as wire_domain
from src.report.wire.domain import WireNode, WireSubscriber


class SourceNode(Node, WireSubscriber):
    title: str
    wires: list[wire_domain.WireNode] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def follow_wires(self, wires: set[WireNode]):
        self.wires.extend(wires)
        self._on_subscribed(wires)
        self._events.append(WireNodesAppended(wire_nodes=list(wires), source_node=self))

    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        self._events.append(WireUpdated(source=self, old_value=old_value, new_value=new_value))


class SourceSubscriber(ABC):
    @abstractmethod
    def follow_source(self, source: SourceNode):
        raise NotImplemented

    @abstractmethod
    def on_wires_appended(self, wire: list[WireNode]):
        raise NotImplemented

    @abstractmethod
    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        raise NotImplemented


class CreateSourceNode(Command):
    title: str
    uuid: UUID = Field(default_factory=uuid4)


class WireNodesAppended(Event):
    wire_nodes: list[wire_domain.WireNode]
    source_node: SourceNode
    uuid: UUID = Field(default_factory=uuid4)


class WireUpdated(NodeUpdated):
    source: SourceNode
    old_value: WireNode
    new_value: WireNode
    uuid: UUID = Field(default_factory=uuid4)
