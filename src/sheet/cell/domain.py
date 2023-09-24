from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellValue
from src.node.domain import Node, Event


class CellNode(Node):
    index: tuple[int, int]
    value: CellValue
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def follow(self, pubs: set['Node']):
        if len(pubs) != 1:
            raise Exception
        for pub in pubs:
            if not hasattr(pub, "value"):
                raise Exception
            self.value = pub.value
        self._on_subscribed(pubs)
        self._on_updated()

    def update(self, old_value: 'Node', new_value: 'Node'):
        if not hasattr(new_value, "value"):
            raise Exception
        self.value = new_value.value
        self._on_updated()
