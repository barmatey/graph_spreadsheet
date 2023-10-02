from abc import abstractmethod, ABC
from sortedcontainers import SortedList
from uuid import UUID, uuid4
from pydantic import Field, PrivateAttr

from src.core.pydantic_model import Model
from src.helpers.decorators import singleton


class Command(Model):
    uuid: UUID


class Event(Model):
    uuid: UUID
    priority: int


class Subscriber(ABC):
    @abstractmethod
    def parse_events(self) -> list[Event]:
        raise NotImplemented


@singleton
class EventQueue:
    def __init__(self):
        self._events = SortedList(key=lambda x: x.priority)
        self._pubsub_updated_events = {}
        self._uniques = {}

    def append(self, event: Event, unique=False):
        if unique:
            self._uniques[event.uuid] = event
        if isinstance(event, PubsubUpdated):
            key = type(event)
            if self._pubsub_updated_events.get(key) is None:
                self._pubsub_updated_events[key] = event
            else:
                self._pubsub_updated_events[key].old_value = event.new_value
        else:
            self._events.add(event)

    def parse_events(self) -> SortedList[Event]:
        events = self._events
        for event in self._uniques.values():
            events.add(event)
        for event in self._pubsub_updated_events.values():
            events.add(event)
        self._events = SortedList(key=lambda x: x.priority)
        self._pubsub_updated_events = {}
        self._uniques = {}
        return events


class Pubsub(Model):
    uuid: UUID
    _events = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._events = EventQueue()

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def _on_subscribed(self, pubs: set['Pubsub']):
        self._events.append(NodeSubscribed(sub=self, pubs=pubs))

    def _on_updated(self, event: 'PubsubUpdated'):
        self._events.append(event)


class NodeSubscribed(Event):
    pubs: set[Pubsub]
    sub: Pubsub
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class PubsubUpdated(Event):
    old_value: Pubsub
    new_value: Pubsub
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
