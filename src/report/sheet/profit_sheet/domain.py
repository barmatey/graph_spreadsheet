from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from src.node.domain import Event, Command
from src.report.formula.mapper.domain import MapperSubscriber, MapperNode
from src.report.formula.period.domain import PeriodSubscriber, PeriodNode
from src.report.source.domain import SourceSubscriber, Source
from src.report.wire.domain import WireNode
from src.spreadsheet.cell.domain import SheetCell, CellUpdated
from src.spreadsheet.sheet.domain import Sheet, SheetSubscriber


class FinrepSheet(Sheet, SheetSubscriber):
    uuid: UUID = Field(default_factory=uuid4)

    def follow_sheet(self, sheet: Sheet):
        self._on_subscribed({sheet})

    def on_rows_appended(self, rows: list[list[SheetCell]]):
        pass


class ProfitPeriodCell(SheetCell, PeriodSubscriber):
    uuid: UUID = Field(default_factory=uuid4)

    def follow_periods(self, pubs: set[PeriodNode]):
        for pub in pubs:
            self.value = pub.to_date

    def on_period_updated(self, old_value: PeriodNode, new_value: PeriodNode):
        self.value = new_value.to_date


class ProfitMapperCell(SheetCell, MapperSubscriber):
    uuid: UUID = Field(default_factory=uuid4)

    def follow_mappers(self, pubs: set[MapperNode]):
        old = self.model_copy(deep=True)
        for pub in pubs:
            self.value = pub.filter_by[pub.ccols[self.index[1]]]
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def on_mapper_update(self, old_value: MapperNode, new_value: MapperNode):
        old = self.model_copy(deep=True)
        self.value = new_value.filter_by[new_value.ccols[self.index[1]]]
        self._on_updated(CellUpdated(old_value=old, new_value=self))


class ProfitCell(SheetCell, MapperSubscriber, PeriodSubscriber, SourceSubscriber):
    value: float
    mapper: MapperNode | None = None
    period: PeriodNode | None = None
    uuid: UUID = Field(default_factory=uuid4)
    _recalculated: bool = False

    def follow_source(self, source: Source):
        old_value = self.model_copy(deep=True)
        for w in source.wires:
            if self.mapper.is_filtred(w) and self.period.is_filtred(w):
                self.value += w.amount
        self._on_subscribed({source})
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_wires_appended(self, wires: list[WireNode]):
        old_value = self.model_copy(deep=True)
        for wire in wires:
            if self.mapper.is_filtred(wire) and self.period.is_filtred(wire):
                self.value += wire.amount
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        old = self.model_copy(deep=True)
        if self.mapper.is_filtred(old_value) and self.period.is_filtred(old_value):
            self.value -= old_value.amount
        if self.mapper.is_filtred(new_value) and self.period.is_filtred(new_value):
            self.value += new_value.amount
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def follow_mappers(self, pubs: set[MapperNode]):
        for pub in pubs:
            self.mapper = pub

    def on_mapper_update(self, old_value: MapperNode, new_value: MapperNode):
        self.mapper = new_value
        self._recalculated = True

    def follow_periods(self, pubs: set[PeriodNode]):
        for pub in pubs:
            self.period = pub

    def on_period_updated(self, old_value: PeriodNode, new_value: PeriodNode):
        self.period = new_value
        self._recalculated = True

    def recalculate(self, wires: set[WireNode]):
        old_value = self.model_copy(deep=True)
        self.value = 0
        for wire in wires:
            if self.mapper.is_filtred(wire):
                self.value += wire.amount
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def parse_events(self) -> list[Event]:
        events = super().parse_events()
        if self._recalculated:
            events.append(ProfitCellRecalculateRequested(node=self))
            self._recalculated = False
        return events


class CreateProfitSheetNode(Command):
    source_id: UUID
    group_id: UUID
    start_date: datetime
    end_date: datetime
    period: int = 3
    freq: Literal['H', 'D', 'M', 'Y'] = 'M'
    uuid: UUID = Field(default_factory=uuid4)


class CreateProfitCellNode(Command):
    period_node_id: UUID
    mapper_node_id: UUID
    source_node_id: UUID
    uuid: UUID = Field(default_factory=uuid4)


class ProfitCellRecalculateRequested(Event):
    node: ProfitCell
    uuid: UUID = Field(default_factory=uuid4)
