from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable
from src.core.pydantic_model import Model
from src.node.domain import Command
from src.report.source.domain import SourceSubscriber, Source
from src.report.wire.domain import Ccol, WireNode
from src.spreadsheet.cell.domain import CellTablePublisher, SheetCell
from src.spreadsheet.sheet import domain as sheet_domain


class PlanItems(Model):
    ccols: list[Ccol]
    uniques: dict[str, int] = Field(default_factory=dict)
    uuid: UUID = Field(default_factory=uuid4)


class GroupSheetNode(sheet_domain.Sheet, SourceSubscriber):
    plan_items: PlanItems
    uuid: UUID = Field(default_factory=uuid4)

    def follow_source(self, source: Source):
        self.on_wires_appended(source.wires)
        self._on_subscribed({source})

    def on_wires_appended(self, wires: list[WireNode]):
        rows = []
        for wire in wires:
            row = [wire.__getattribute__(ccol) for ccol in self.plan_items.ccols]
            key = str(row)
            if self.plan_items.uniques.get(key) is None:
                self.plan_items.uniques[key] = 1
                rows.append([SheetCell(index=(self.size[0], j), value=value) for j, value in enumerate(row)])
            else:
                self.plan_items.uniques[key] += 1
        self.append_rows(rows)

    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        old_row = [old_value.__getattribute__(ccol) for ccol in self.plan_items.ccols]
        old_key = str(old_row)

        new_row = [new_value.__getattribute__(ccol) for ccol in self.plan_items.ccols]
        new_key = str(new_row)

        # Drop old value
        rows_to_delete = []
        self.plan_items.uniques[old_key] -= 1
        if self.plan_items.uniques[old_key] == 0:
            del self.plan_items.uniques[old_key]
            for i, row in enumerate(self.table):
                if str([v.value for v in row]) == old_key:
                    rows_to_delete.append(i)
        if rows_to_delete:
            self.delete_rows(rows_to_delete)

        if self.plan_items.uniques.get(new_key) is not None:
            self.plan_items.uniques[new_key] += 1
        else:
            self.plan_items.uniques[new_key] = 1
            self.append_rows([SheetCell(index=(self.size[0], j), value=value) for j, value in enumerate(new_row)])


class CreateGroupSheetNode(Command):
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)


class GetSheetById(Command):
    uuid: UUID
