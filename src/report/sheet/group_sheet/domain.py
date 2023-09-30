from uuid import UUID, uuid4

from pydantic import Field

from src.core.pydantic_model import Model
from src.pubsub.domain import Command
from src.report.source.domain import SourceSubscriber, Source
from src.report.wire.domain import Ccol, Wire
from src.spreadsheet.cell.domain import SheetCell
from src.spreadsheet.sheet import domain as sheet_domain
from src.spreadsheet.sindex.handlers import Sindex


class PlanItems(Model):
    ccols: list[Ccol]
    uniques: dict[str, int] = Field(default_factory=dict)
    uuid: UUID = Field(default_factory=uuid4)


class GroupSheet(sheet_domain.Sheet, SourceSubscriber):
    plan_items: PlanItems
    uuid: UUID = Field(default_factory=uuid4)

    def follow_source(self, source: Source):
        self.on_wires_appended(source.wires)
        self._on_subscribed({source})

    def on_wires_appended(self, wires: list[Wire]):
        table = []
        rows: list[Sindex] = []
        for wire in wires:
            cells = [wire.__getattribute__(ccol) for ccol in self.plan_items.ccols]
            key = str(cells)
            if self.plan_items.uniques.get(key) is None:
                row_sindex = Sindex(position=self.size[0])
                rows.append(row_sindex)
                self.plan_items.uniques[key] = 1
                table.append([
                    SheetCell(row_index=row_sindex, col_index=Sindex(position=j), value=value)
                    for j, value in enumerate(cells)
                ])
            else:
                self.plan_items.uniques[key] += 1
        self.append_rows(rows, table)

    def on_wire_updated(self, old_value: Wire, new_value: Wire):
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
            self.append_rows([
                SheetCell(row_index=Sindex(position=self.size[0]), col_index=Sindex(position=j), value=value)
                for j, value in enumerate(new_row)
            ])


class CreateGroupSheet(Command):
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)


class GetSheetById(Command):
    uuid: UUID
