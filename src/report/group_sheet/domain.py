from uuid import UUID, uuid4

from pydantic import Field

from src.core.cell import CellTable
from src.core.pydantic_model import Model
from src.node.domain import Command, Node, Event
from src.report.wire.domain import Ccol, WireNode
from src.spreadsheet.sheet import domain as sheet_domain


class PlanItems(Model):
    ccols: list[Ccol]
    uniques: dict[str, int] = Field(default_factory=dict)
    value: CellTable = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)


class GroupSheetNode(sheet_domain.SheetNode):
    plan_items: PlanItems
    uuid: UUID = Field(default_factory=uuid4)
    table: CellTable = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)

    def __follow_wire(self, pub: WireNode):
        row = [pub.__getattribute__(ccol) for ccol in self.plan_items.ccols]
        key = str(row)
        if self.plan_items.uniques.get(key) is None:
            self.plan_items.value.append(row)
            self.plan_items.uniques[key] = 1
        else:
            self.plan_items.uniques[key] += 1

    def __update_wire(self, old_value: WireNode, new_value: WireNode):
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
            return
        self.plan_items.uniques[new_key] = 1
        utable.append(new_row)

        self._on_updated()
        return

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, WireNode):
                self.__follow_wire(pub)
            else:
                raise TypeError(f"invalid type: {type(pub)}")

        self._on_updated()
        self._on_subscribed(pubs)

    def update(self, old_value: 'Node', new_value: 'Node'):
        if isinstance(old_value, WireNode) and isinstance(new_value, WireNode):
            self.__update_wire(old_value, new_value)
        else:
            raise TypeError(f"Expected type is SourceNode but real type is {type(new_value)}")


class CreateGroupSheetNode(Command):
    title: str
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)


class GetSheetById(Command):
    uuid: UUID
