from uuid import UUID, uuid4
from pydantic import Field

from src.node.domain import Command, Event, Node
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.mapper.domain import MapperSubscriber, MapperNode
from src.report.formula.period import domain as period_domain
from src.report.formula.period.domain import PeriodSubscriber, PeriodNode
from src.report.source.domain import SourceSubscriber, SourceNode
from src.report.wire import domain as wire_domain
from src.report.wire.domain import WireNode
from src.spreadsheet.cell.domain import SheetCell


class ProfitCellNode(SheetCell, MapperSubscriber, PeriodSubscriber, SourceSubscriber):
    value: float
    mapper: mapper_domain.MapperNode | None = None
    period: period_domain.PeriodNode | None = None
    uuid: UUID = Field(default_factory=uuid4)
    _recalculated: bool = False

    def follow_source(self, source: SourceNode):
        for w in source.wires:
            if self.mapper.is_filtred(w) and self.period.is_filtred(w):
                self.value += w.amount
        self._on_subscribed({source})

    def on_wires_appended(self, wires: list[WireNode]):
        for wire in wires:
            if self.mapper.is_filtred(wire) and self.period.is_filtred(wire):
                self.value += wire.amount

    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        self.value -= old_value.amount
        if self.mapper.is_filtred(new_value) and self.period.is_filtred(new_value):
            self.value += new_value.amount

    def follow_mappers(self, pubs: set[MapperNode]):
        for pub in pubs:
            self.mapper = pub
            self._recalculated = True

    def on_mapper_update(self, old_value: MapperNode, new_value: MapperNode):
        self.mapper = new_value
        self._recalculated = True

    def follow_periods(self, pubs: set[PeriodNode]):
        for pub in pubs:
            self.period = pub
            self._recalculated = True

    def on_period_updated(self, old_value: PeriodNode, new_value: PeriodNode):
        self.period = new_value
        self._recalculated = True

    def recalculate(self, wires: set[wire_domain.WireNode]):
        self.value = 0
        for wire in wires:
            if self.mapper.is_filtred(wire):
                self.value += wire.amount


class CreateProfitCellNode(Command):
    period_node_id: UUID
    mapper_node_id: UUID
    source_node_id: UUID
    uuid: UUID = Field(default_factory=uuid4)


class ProfitCellRecalculateRequested(Event):
    node: ProfitCellNode
    uuid: UUID = Field(default_factory=uuid4)
