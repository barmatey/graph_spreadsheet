from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, Event, Command


class SourceNode(Node):
    title: str
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def update(self, old_value: 'Node', new_value: 'Node'):
        self._on_updated()

    def follow(self, pubs: set['Node']):
        self._on_updated()
        self._on_subscribed(pubs)


class CreateSourceNode(Command):
    title: str
    uuid: UUID = Field(default_factory=uuid4)
