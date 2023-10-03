from abc import abstractmethod, ABC

from loguru import logger
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

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return self.__str__()


class Subscriber(ABC):
    pass


@singleton
class EventQueue:
    def __init__(self):
        self._events = {}
        self._order = SortedList(key=lambda x: x[1])

    def append(self, event: Event, unique=False, unique_key: str = None):
        logger.debug(f"APPEND: {event}:{event.priority}")
        if unique:
            if unique_key is None:
                raise Exception("unique key is None")
            if self._events.get(unique_key) is None:
                self._order.add((unique_key, event.priority))
            else:
                self._order.remove((unique_key, event.priority))
                self._order.add((unique_key, event.priority))
            self._events[unique_key] = event

        elif isinstance(event, PubsubUpdated):
            key = type(event)
            if self._events.get(key) is None:
                self._events[key] = event
                self._order.add((key, event.priority))
            else:
                self._events[key].old_value = event.new_value
                self._order.remove((key, event.priority))
                self._order.add((key, event.priority))
        else:
            self._events[event.uuid] = event
            self._order.add((event.uuid, event.priority,))

    @property
    def empty(self) -> bool:
        return len(self._order) == 0

    def pop_start(self):
        key = self._order.pop(0)[0]
        event = self._events.pop(key)
        logger.debug(f"EXTRACT: {event}:{event.priority}")
        return event


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

    def _on_followed(self, pubs: set['Pubsub']):
        self._events.append(PubsubSubscribed(sub=self, pubs=pubs))

    def _on_updated(self, event: 'PubsubUpdated'):
        self._events.append(event)


class PubsubSubscribed(Event):
    pubs: set[Pubsub]
    sub: Pubsub
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class PubsubUpdated(Event):
    old_value: Pubsub
    new_value: Pubsub
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
