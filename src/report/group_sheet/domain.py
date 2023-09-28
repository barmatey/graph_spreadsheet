from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable
from src.core.pydantic_model import Model
from src.node.domain import Command, Node
from src.report.source.domain import SourceSubscriber, SourceNode
from src.report.wire.domain import Ccol, WireNode
from src.spreadsheet.cell.domain import CellTablePublisher, SheetCell
from src.spreadsheet.sheet import domain as sheet_domain


class PlanItems(Model):
    ccols: list[Ccol]
    uniques: dict[str, int] = Field(default_factory=dict)
    value: CellTable = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)


class GroupSheetNode(sheet_domain.SheetNode, SourceSubscriber, CellTablePublisher):
    plan_items: PlanItems
    uuid: UUID = Field(default_factory=uuid4)

    def follow_source(self, source: SourceNode):
        self.on_wires_appended(source.wires)
        self._on_subscribed({source})

    def on_wires_appended(self, wires: list[WireNode]):
        for wire in wires:
            row = [wire.__getattribute__(ccol) for ccol in self.plan_items.ccols]
            key = str(row)
            row = [SheetCell(index=(self.size[0], j), value=value) for j, value in enumerate(row)]
            if self.plan_items.uniques.get(key) is None:
                self.append_row(row)
                self.plan_items.uniques[key] = 1
            else:
                self.plan_items.uniques[key] += 1

    def on_wire_updated(self, old_value: WireNode, new_value: WireNode):
        old_row = [old_value.__getattribute__(ccol) for ccol in self.plan_items.ccols]
        old_key = str(old_row)

        new_row = [new_value.__getattribute__(ccol) for ccol in self.plan_items.ccols]
        new_key = str(new_row)

        # Drop old value
        utable = self.plan_items.value
        self.plan_items.uniques[old_key] -= 1
        if self.plan_items.uniques[old_key] == 0:
            del self.plan_items.uniques[old_key]
            for i, row in enumerate(utable):
                if str(row) == old_key:
                    del utable[i]

        if self.plan_items.uniques.get(new_key) is not None:
            self.plan_items.uniques[new_key] += 1
        else:
            self.plan_items.uniques[new_key] = 1
            utable.append(new_row)

    def get_cell_table(self) -> CellTable:
        return self.plan_items.value


class CreateGroupSheetNode(Command):
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)


class GetSheetById(Command):
    uuid: UUID
