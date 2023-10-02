from abc import abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event, Pubsub, Subscriber


class Sindex(Pubsub):
    position: int
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SindexCreated(entity=self))

    def delete(self):
        self._events.append(SindexDeleted(entity=self), unique=True)


class SindexSubscriber(Subscriber):
    @abstractmethod
    def on_sindex_deleted(self, pub: Sindex):
        raise NotImplemented


class SindexCreated(Event):
    entity: Sindex
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class SindexDeleted(Event):
    entity: Sindex
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
