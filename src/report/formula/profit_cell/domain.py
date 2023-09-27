from uuid import UUID, uuid4

from pydantic import Field

from src.node.domain import Node, Command, Event
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.period import domain as period_domain
from src.report.source.domain import SourceSubscriber, SourceNode
from src.report.wire import domain as wire_domain
from src.report.source import domain as source_domain


class ProfitCellNode(Node, SourceSubscriber):
    value: float
    mapper: mapper_domain.MapperNode | None = None
    period: period_domain.PeriodNode | None = None
    uuid: UUID = Field(default_factory=uuid4)

    def follow_source(self, source:  SourceNode):
        for w in source.wires:
            if self.mapper.is_filtred(w) and self.period.is_filtred(w):
                self.value += w.amount
        self._on_subscribed({source})
        self._on_updated()

    def follow(self, pubs: set['Node']):
        followed = pubs.copy()
        for pub in pubs:
            if isinstance(pub, wire_domain.WireNode):
                if self.mapper.is_filtred(pub) and self.period.is_filtred(pub):
                    self.value += pub.amount
            elif isinstance(pub, mapper_domain.MapperNode):
                self.mapper = pub
                self._events.append_unique_event(ProfitCellRecalculateRequested(node=self))
            elif isinstance(pub, period_domain.PeriodNode):
                self.period = pub
                self._events.append_unique_event(ProfitCellRecalculateRequested(node=self))
            else:
                raise TypeError(f"real type is {type(pub)}")
        self._on_subscribed(followed)
        self._on_updated()

    def update(self, old_value: 'Node', new_value: 'Node'):
        if isinstance(old_value, wire_domain.WireNode) and isinstance(new_value, wire_domain.WireNode):
            self.value -= old_value.amount
            if self.mapper.is_filtred(new_value) and self.period.is_filtred(new_value):
                self.value += new_value.amount
        elif isinstance(old_value, mapper_domain.MapperNode) and isinstance(new_value, mapper_domain.MapperNode):
            self.mapper = new_value
            self._events.append_unique_event(ProfitCellRecalculateRequested(node=self))
        elif isinstance(old_value, period_domain.PeriodNode) and isinstance(new_value, period_domain.PeriodNode):
            self.period = new_value
            self._events.append_unique_event(ProfitCellRecalculateRequested(node=self))
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
