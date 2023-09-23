from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, Event, Command


class SourceNode(Node):
    title: str
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def on_pub_updated(self, old_value: 'Node', new_value: 'Node'):
        self._notify()

    def on_subscribed(self, pubs: set['Node']):
        self._notify()


class CreateSourceNode(Command):
    title: str
    uuid: UUID = Field(default_factory=uuid4)
