from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, Command, Event
from src.formula.mapper import domain as mapper_domain
from src.formula.period import domain as period_domain
from src.wire import domain as wire_domain


class ProfitCellNode(Node):
    value: float
    mapper: mapper_domain.MapperNode | None = None
    period: period_domain.PeriodNode | None = None
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, wire_domain.WireNode):
                if self.mapper.is_filtred(pub) and self.period.is_filtred(pub):
                    self.value += pub.amount
            elif isinstance(pub, mapper_domain.MapperNode):
                self.mapper = pub
                self.events.append(ProfitCellRecalculateRequested(node=self))
            elif isinstance(pub, period_domain.PeriodNode):
                self.period = pub
                self.events.append(ProfitCellRecalculateRequested(node=self))
            else:
                raise TypeError(f"real type is {type(pub)}")
        self._on_subscribed(pubs)
        self._on_updated()

    def update(self, old_value: 'Node', new_value: 'Node'):
        if isinstance(old_value, wire_domain.WireNode) and isinstance(new_value, wire_domain.WireNode):
            self.value -= old_value.amount
            if self.mapper.is_filtred(new_value) and self.period.is_filtred(new_value):
                self.value += new_value.amount
        elif isinstance(old_value, mapper_domain.MapperNode) and isinstance(new_value, mapper_domain.MapperNode):
            self.mapper = new_value
            self.events.append(ProfitCellRecalculateRequested(node=self))
        elif isinstance(old_value, period_domain.PeriodNode) and isinstance(new_value, period_domain.PeriodNode):
            self.period = new_value
            self.events.append(ProfitCellRecalculateRequested(node=self))
        else:
            raise TypeError(f"real type is {type(old_value)}, {type(new_value)}")
        self._on_updated()

    def recalculate(self, wires: set[wire_domain.WireNode]):
        self.value = 0
        for wire in wires:
            if self.mapper.is_filtred(wire):
                self.value += wire.amount
        self._on_updated()


class CreateProfitCellNode(Command):
    period_node_id: UUID
    mapper_node_id: UUID
    source_node_id: UUID
    uuid: UUID = Field(default_factory=uuid4)


class ProfitCellRecalculateRequested(Event):
    node: ProfitCellNode
    uuid: UUID = Field(default_factory=uuid4)
