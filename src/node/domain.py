from abc import abstractmethod
from collections import OrderedDict
from uuid import UUID, uuid4
from pydantic import Field, PrivateAttr

from src.core.pydantic_model import Model


class Command(Model):
    uuid: UUID


class Event(Model):
    uuid: UUID


class EventQueue:
    def __init__(self):
        self._events = OrderedDict()

    def append_node_updated_event(self, event: 'NodeUpdated'):
        key = "node_updated_event"
        if self._events.get(key) is None:
            self._events[key] = event
        else:
            old: 'NodeUpdated' = self._events.pop(key)
            self._events[key] = NodeUpdated(old_value=old.old_value, new_value=event.new_value)

    def append_unique_event(self, event: Event):
        key = type(event)
        if self._events.get(key) is not None:
            self._events.pop(key)
        self._events[key] = event

    def append_event(self, event: Event):
        self._events[event.uuid] = event

    def parse_events(self) -> list[Event]:
        events = self._events
        self._events = OrderedDict()
        return list(events.values())


class Node(Model):
    uuid: UUID
    _events: EventQueue = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._events = EventQueue()

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
        self._events.append_node_updated_event(NodeUpdated(old_value=self.model_copy(deep=True), new_value=self))

    def _on_subscribed(self, pubs: set['Node']):
        self._events.append_event(NodeSubscribed(sub=self, pubs=pubs))

    def set_node_fields(self, data: dict):
        for key, value in data.items():
            self.__setattr__(key, value)

    def parse_events(self) -> list[Event]:
        return self._events.parse_events()


class NodeUpdated(Event):
    pass


class NodeSubscribed(Event):
    pubs: set[Node]
    sub: Node
    uuid: UUID = Field(default_factory=uuid4)
