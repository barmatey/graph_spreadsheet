from uuid import UUID, uuid4

from pydantic import Field

from src.core.pydantic_model import Model


class Sindex(Model):
    position: int
    uuid: UUID = Field(default_factory=uuid4)
