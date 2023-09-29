from abc import abstractmethod
from collections import OrderedDict
from typing import Optional
from uuid import UUID, uuid4
from pydantic import Field, PrivateAttr

from src.core.pydantic_model import Model


class Command(Model):
    uuid: UUID


class Event(Model):
    uuid: UUID


class Node(Model):
    uuid: UUID
    _events = PrivateAttr()
    _updated: Optional['Pubsub'] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._events = []
        self._updated = None

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def _on_subscribed(self, pubs: set['Node']):
        self._events.append(NodeSubscribed(sub=self, pubs=pubs))

    def _on_updated(self, event: 'Pubsub'):
        if self._updated is None:
            self._updated = event
        else:
            self._updated.new_value = event.new_value

    def parse_events(self) -> list[Event]:
        events: list[Event] = self._events
        self._events = []
        if self._updated is not None:
            events.append(self._updated)
            self._updated = None
        return events


class NodeSubscribed(Event):
    pubs: set[Node]
    sub: Node
    uuid: UUID = Field(default_factory=uuid4)


class Pubsub(Event):
    old_value: Node
    new_value: Node
    uuid: UUID = Field(default_factory=uuid4)
