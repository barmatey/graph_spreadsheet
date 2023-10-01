from uuid import UUID, uuid4

from pydantic import Field

from src.pubsub.domain import Event, Pubsub


class Sindex(Pubsub):
    position: int
    uuid: UUID = Field(default_factory=uuid4)

    def __init__(self, **data):
        super().__init__(**data)
        self._events.append(SindexCreated(entity=self))


class SindexCreated(Event):
    entity: Sindex
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10
