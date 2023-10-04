from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event, Pubsub


def size_factory():
    return 0, 0


class Sheet(Pubsub):
    size: tuple[int, int] = Field(default_factory=size_factory)
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SheetCreated(entity=self))

    def __str__(self):
        return f"{self.__class__.__name__}(size={self.size})"


class SheetCreated(Event):
    entity: Sheet
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


