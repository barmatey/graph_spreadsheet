from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Pubsub, Event, Command, PubsubUpdated
from src.report.wire import domain as wire_domain
from src.report.wire.domain import Wire, WireSubscriber


class Source(Pubsub, WireSubscriber):
    title: str
    wires: list[wire_domain.Wire] = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SourceCreated(entity=self))

    def follow_wires(self, wires: set[Wire]):
        self.wires.extend(wires)
        self._on_subscribed(wires)
        self._events.append(WiresAppended(wire_nodes=list(wires), source_node=self))

    def on_wire_updated(self, old_value: Wire, new_value: Wire):
        self._events.append(WireUpdated(source=self, old_value=old_value, new_value=new_value))


class SourceSubscriber(ABC):
    @abstractmethod
    def follow_source(self, source: Source):
        raise NotImplemented

    @abstractmethod
    def on_wires_appended(self, wire: list[Wire]):
        raise NotImplemented

    @abstractmethod
    def on_wire_updated(self, old_value: Wire, new_value: Wire):
        raise NotImplemented


class CreateSource(Command):
    title: str
    uuid: UUID = Field(default_factory=uuid4)


class SourceCreated(Event):
    entity: Source
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class WiresAppended(Event):
    wire_nodes: list[wire_domain.Wire]
    source_node: Source
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class WireUpdated(PubsubUpdated):
    source: Source
    old_value: Wire
    new_value: Wire
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
