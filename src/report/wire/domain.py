import typing
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.pubsub.domain import Pubsub, PubsubUpdated, Event, Command

Ccol = typing.Literal['currency', 'sender', 'receiver', 'sub1', 'sub2', 'comment']


class Wire(Pubsub):
    sender: float
    receiver: float
    amount: float
    currency: str = "RUB"
    date: datetime = Field(default_factory=datetime.now)
    sub1: str = ""
    sub2: str = ""
    comment: str = ""
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(WireCreated(entity=self))

    def set_node_fields(self, **kwargs):
        old_value = self.model_copy(deep=True)
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        self._on_updated(WireUpdated(old_value=old_value, new_value=self))


class WireSubscriber(ABC):
    @abstractmethod
    def follow_wires(self, wires: set[Wire]):
        raise NotImplemented

    @abstractmethod
    def on_wire_updated(self, old_value: Wire, new_value: Wire):
        raise NotImplemented


class CreateWire(Command):
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


class WireCreated(Event):
    entity: Wire
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class WireUpdated(PubsubUpdated):
    old_value: Wire
    new_value: Wire
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
