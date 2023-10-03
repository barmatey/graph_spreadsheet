from abc import abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event, Pubsub, Subscriber


class SindexSubscriber(Subscriber):
    @abstractmethod
    def follow_sindexes(self, pubs: set['Sindex']):
        raise NotImplemented

    @abstractmethod
    def on_sindex_deleted(self, pub: 'Sindex'):
        raise NotImplemented


class Sindex(Pubsub, SindexSubscriber):
    position: int
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SindexCreated(entity=self))

    def follow_sindexes(self, pubs: set['Sindex']):
        self._on_subscribed(pubs)

    def on_sindex_deleted(self, pub: 'Sindex'):
        self.delete()

    def delete(self):
        self._events.append(SindexDeleted(entity=self))


class SindexCreated(Event):
    entity: Sindex
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class SindexDeleted(Event):
    entity: Sindex
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
