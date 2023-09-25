from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command, Event
from src.report.wire import domain as wire_domain
from src.sheet.formula.utable import domain as utable_domain


class MapperNode(Node):
    index: int
    filter_by: dict = Field(default_factory=dict)
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def is_filtred(self, wire: wire_domain.WireNode) -> bool:
        return all([wire.__getattribute__(key) == value for key, value in self.filter_by.items()])

    def update(self, old_value: 'Node', new_value: 'Node'):
        if not isinstance(new_value, utable_domain.UtableNode):
            raise TypeError(type(new_value))
        if not isinstance(old_value, utable_domain.UtableNode):
            raise TypeError(type(old_value.old_value))
        self._on_updated()

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if not isinstance(pub, utable_domain.UtableNode):
                raise TypeError(f"real type is {type(pub)}")
            index = self.index
            filter_by = {}
            for j, ccol in enumerate(pub.ccols):
                filter_by[ccol] = pub.value[index][j]
            self.filter_by = filter_by

        self._on_subscribed(pubs)
        self._on_updated()


class CreateMapperNode(Command):
    utable_id: UUID
    row_index: int
    uuid: UUID = Field(default_factory=uuid4)

