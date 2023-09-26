from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, Event, Command
from src.report.wire import  domain as wire_domain


class SourceNode(Node):
    title: str
    wires: list[wire_domain.WireNode] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def append_wires(self, wires: list[wire_domain.WireNode]):
        self.wires.extend(wires)
        self.events.append(WireNodesAppended(wire_nodes=wires, source_node=self))

    def update(self, old_value: 'Node', new_value: 'Node'):
        self._on_updated()

    def follow(self, pubs: set['Node']):
        self._on_subscribed(pubs)
        self._on_updated()


class CreateSourceNode(Command):
    title: str
    uuid: UUID = Field(default_factory=uuid4)


class WireNodesAppended(Event):
    wire_nodes: list[wire_domain.WireNode]
    source_node: SourceNode
    uuid: UUID = Field(default_factory=uuid4)
