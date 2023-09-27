from abc import abstractmethod
from collections import OrderedDict
from uuid import UUID, uuid4
from pydantic import Field

from src.core.pydantic_model import Model


class Command(Model):
    uuid: UUID


class Event(Model):
    uuid: UUID


class Node(Model):
    uuid: UUID
    events: 'EventQueue'

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def update(self, old_value: 'Node', new_value: 'Node'):
        raise NotImplemented

    @abstractmethod
    def follow(self, pubs: set['Node']):
        raise NotImplemented

    def as_child(self, pubs: set['Node']):
        """Subscribe on publishers without typechecking and without changing state"""
        self._on_subscribed(pubs)

    def _on_updated(self):
        self.events.append_node_updated_event(NodeUpdated(old_value=self.model_copy(deep=True), new_value=self))

    def _on_subscribed(self, pubs: set['Node']):
        self.events.append(NodeSubscribed(sub=self, pubs=pubs))

    def set_node_fields(self, data: dict):
        old_value = self.model_copy(deep=True)
        for key, value in data.items():
            self.__setattr__(key, value)
        self.events.append(NodeUpdated(old_value=old_value, new_value=self))

    def parse_events(self) -> list[Event]:
        return self.events.parse_events()


class NodeUpdated(Event):
    old_value: Node
    new_value: Node
    uuid: UUID = Field(default_factory=uuid4)


class NodeSubscribed(Event):
    pubs: set[Node]
    sub: Node
    uuid: UUID = Field(default_factory=uuid4)


class EventQueue:
    def __init__(self):
        self._events = OrderedDict()

    def append_node_updated_event(self, event: NodeUpdated):
        key = type(event)
        if self._events.get(key) is None:
            self._events[key] = event
        else:
            old = self._events.pop(key)
            self._events[key] = NodeUpdated(old_value=old.old_value, new_value=event.new_value)

    def append(self, event: Event):
        self._events[event.uuid] = event

    def parse_events(self) -> list[Event]:
        events = self._events
        self._events = OrderedDict()
        return list(events.values())
