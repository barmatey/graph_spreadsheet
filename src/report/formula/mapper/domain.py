from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command, Event
from src.report.wire import domain as wire_domain
from src.report.wire.domain import Ccol
from src.spreadsheet.cell import domain as cell_domain
from src.spreadsheet.sheet import domain as sheet_domain


class MapperNode(Node):
    ccols: list[Ccol]
    filter_by: dict = Field(default_factory=dict)
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def __str__(self):
        return f"MapperNode(filter_by={self.filter_by})"

    def is_filtred(self, wire: wire_domain.WireNode) -> bool:
        return all([wire.__getattribute__(key) == value for key, value in self.filter_by.items()])

    def update(self, old_value: 'Node', new_value: 'Node'):
        if not isinstance(old_value, cell_domain.CellNode) and isinstance(new_value, cell_domain.CellNode):
            raise TypeError(f"invalid types: {type(old_value)}, {type(new_value)}")
        key = self.ccols[new_value.index[1]]
        value = new_value.value
        self.filter_by[key] = value
        self._on_updated()

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, cell_domain.CellNode):
                key = self.ccols[pub.index[1]]
                value = pub.value
                self.filter_by[key] = value
            elif isinstance(pub, sheet_domain.SheetNode):
                pass
            else:
                raise TypeError(f"invalid type: {type(pub)}")

        self._on_subscribed(pubs)
        self._on_updated()


class CreateMapperNode(Command):
    utable_id: UUID
    row_index: int
    uuid: UUID = Field(default_factory=uuid4)
