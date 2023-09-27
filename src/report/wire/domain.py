import typing
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, NodeUpdated, Event, Command

Ccol = typing.Literal['currency', 'sender', 'receiver', 'sub1', 'sub2', 'comment']


class WireNode(Node):
    currency: str
    date: datetime
    sender: float
    receiver: float
    amount: float
    sub1: str
    sub2: str
    comment: str
    uuid: UUID = Field(default_factory=uuid4)

    def update(self, old_value: 'Node', new_value: 'Node'):
        logger.warning("WireNode parent was updated?")
        self._events.append_node_updated_event(WireUpdated(old_value=self.model_copy(deep=True), new_value=self))

    def follow(self, pubs: set['Node']):
        raise NotImplemented


class WireSubscriber(ABC):
    @abstractmethod
    def follow_wires(self, wires: set[WireNode]):
        raise NotImplemented

    @abstractmethod
    def update_wire(self, old_value: WireNode, new_value: WireNode):
        raise NotImplemented


class CreateWireNode(Command):
    source_id: UUID
    sender: float
    receiver: float
    amount: float
    sub1: str = ""
    sub2: str = ""
    comment: str = ""
    currency: str = "RUB"
    date: datetime = Field(default_factory=datetime.now)
    uuid: UUID = Field(default_factory=uuid4)


class UpdateWire(Command):
    uuid: UUID
    sender: typing.Optional[float] = None
    receiver: typing.Optional[float] = None
    amount: typing.Optional[float] = None
    sub1: typing.Optional[str] = None
    sub2: typing.Optional[str] = None
    comment: typing.Optional[str] = None
    currency: typing.Optional[str] = None
    date: typing.Optional[datetime] = None


class WireUpdated(NodeUpdated):
    old_value: WireNode
    new_value: WireNode
    uuid: UUID= Field(default_factory=uuid4)
