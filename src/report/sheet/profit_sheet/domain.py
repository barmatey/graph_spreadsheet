from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import Field

from src.core.pydantic_model import Model
from src.pubsub.domain import Event, Command
from src.report.formula.mapper.domain import MapperSubscriber, Mapper
from src.report.formula.period.domain import PeriodSubscriber, Period
from src.report.source.domain import SourceSubscriber, Source
from src.report.wire.domain import Wire, Ccol
from src.spreadsheet.cell.domain import SheetCell, CellUpdated
from src.spreadsheet.sheet.domain import Sheet, SheetSubscriber
from src.spreadsheet.sindex.domain import Sindex


class ProfitPeriodCell(SheetCell, PeriodSubscriber):
    uuid: UUID = Field(default_factory=uuid4)

    def follow_periods(self, pubs: set[Period]):
        for pub in pubs:
            self.value = pub.to_date

    def on_period_updated(self, old_value: Period, new_value: Period):
        self.value = new_value.to_date


class ProfitMapperCell(SheetCell, MapperSubscriber):
    uuid: UUID = Field(default_factory=uuid4)

    def follow_mappers(self, pubs: set[Mapper]):
        old = self.model_copy(deep=True)
        for pub in pubs:
            self.value = pub.filter_by[pub.ccols[self.col_index.position]]
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def on_mapper_updated(self, old_value: Mapper, new_value: Mapper):
        old = self.model_copy(deep=True)
        self.value = new_value.filter_by[new_value.ccols[self.col_index.position]]
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def on_mapper_deleted(self, pub: Mapper):
        old = self.model_copy(deep=True)
        self.value = "DELETED"
        self._on_updated(CellUpdated(old_value=old, new_value=self))


class ProfitCell(SheetCell, MapperSubscriber, PeriodSubscriber, SourceSubscriber):
    mapper: Mapper | None = None
    period: Period | None = None
    uuid: UUID = Field(default_factory=uuid4)

    def follow_source(self, source: Source):
        old_value = self.model_copy(deep=True)
        for w in source.wires:
            if self.mapper.is_filtred(w) and self.period.is_filtred(w):
                self.value += w.amount
        self._on_followed({source})
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_wires_appended(self, wires: list[Wire]):
        old_value = self.model_copy(deep=True)
        for wire in wires:
            if self.mapper.is_filtred(wire) and self.period.is_filtred(wire):
                self.value += wire.amount
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))

    def on_wire_updated(self, old_value: Wire, new_value: Wire):
        old = self.model_copy(deep=True)
        if self.mapper.is_filtred(old_value) and self.period.is_filtred(old_value):
            self.value -= old_value.amount
        if self.mapper.is_filtred(new_value) and self.period.is_filtred(new_value):
            self.value += new_value.amount
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def follow_mappers(self, pubs: set[Mapper]):
        for pub in pubs:
            self.mapper = pub
        self._on_followed(pubs)
        self._events.append(ProfitCellRecalculateRequested(node=self), unique=True, unique_key=f"{self.uuid}")

    def on_mapper_updated(self, old_value: Mapper, new_value: Mapper):
        self.mapper = new_value
        self._events.append(ProfitCellRecalculateRequested(node=self), unique=True, unique_key=f"{self.uuid}")

    def on_mapper_deleted(self, pub: Mapper):
        old = self.model_copy(deep=True)
        self.value = "DELETED"
        self._on_updated(CellUpdated(old_value=old, new_value=self))

    def follow_periods(self, pubs: set[Period]):
        for pub in pubs:
            self.period = pub
        self._on_followed(pubs)
        self._events.append(ProfitCellRecalculateRequested(node=self), unique=True, unique_key=f"{self.uuid}")

    def on_period_updated(self, old_value: Period, new_value: Period):
        self.period = new_value
        self._events.append(ProfitCellRecalculateRequested(node=self), unique=True, unique_key=f"{self.uuid}")

    def recalculate(self, wires: set[Wire]):
        old_value = self.model_copy(deep=True)
        self.value = 0
        for wire in wires:
            if self.mapper.is_filtred(wire) and self.period.is_filtred(wire):
                self.value += wire.amount
        self._on_updated(CellUpdated(old_value=old_value, new_value=self))


class ProfitSheetMeta(Model):
    periods: list[Period]
    ccols: list[Literal[Ccol]]
    source_id: UUID
    uuid: UUID = Field(default_factory=uuid4)


class ProfitSheet(Sheet, SheetSubscriber):
    meta: ProfitSheetMeta
    uuid: UUID = Field(default_factory=uuid4)

    def follow_sheet(self, sheet: Sheet):
        self._on_followed({sheet})

    def on_rows_appended(self, rows: list[Sindex], cells: list[list[SheetCell]]):
        self._events.append(GroupSheetRowsAppended(profit_sheet=self, rows=rows, cells=cells))

    def on_rows_deleted(self, rows: list[Sindex]):
        raise NotImplemented


class CreateProfitSheet(Command):
    source_id: UUID
    group_id: UUID
    start_date: datetime
    end_date: datetime
    period: int = 3
    freq: Literal['H', 'D', 'M', 'Y'] = 'M'
    uuid: UUID = Field(default_factory=uuid4)


class GroupSheetRowsAppended(Event):
    profit_sheet: ProfitSheet
    rows: list[Sindex]
    cells: list[list[SheetCell]]
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class ParentSheetRowsDeleted(Event):
    target_sheet: ProfitSheet
    parent_sheet_rows: list[Sindex]
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 10


class ProfitCellRecalculateRequested(Event):
    node: ProfitCell
    uuid: UUID = Field(default_factory=uuid4)
    priority: int = 30
