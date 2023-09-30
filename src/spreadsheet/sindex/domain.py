from uuid import UUID, uuid4

from pydantic import Field

from src.core.pydantic_model import Model
from src.pubsub.domain import Event


class Sindex(Model):
    position: int
    uuid: UUID = Field(default_factory=uuid4)


class SindexCreated(Event):
    entity: Sindex
