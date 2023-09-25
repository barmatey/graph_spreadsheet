from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.core.cell import CellTable
from src.node.domain import Node, Command, Event
from src.report.source.domain import SourceNode
from src.report.wire.domain import Ccol, WireNode


class UtableNode(Node):
    ccols: list[Ccol]
    uniques: dict[str, int] = Field(default_factory=dict)
    value: CellTable = Field(default_factory=list)
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, WireNode):
                row = [pub.__getattribute__(ccol) for ccol in self.ccols]
                key = str(row)
                if self.uniques.get(key) is None:
                    self.value.append(row)
                    self.uniques[key] = 1
                else:
                    self.uniques[key] += 1
            elif isinstance(pub, SourceNode):
                pass
            else:
                raise TypeError(f"invalid type: {type(pub)}")

        self._on_updated()
        self._on_subscribed(pubs)

    def update(self, old_value: 'Node', new_value: 'Node'):
        if isinstance(old_value, SourceNode) and isinstance(new_value, SourceNode):
            logger.warning("UtableNode is not implement update() with SourceNode")
            return

        if isinstance(old_value, WireNode) and isinstance(new_value, WireNode):
            old_row = [old_value.__getattribute__(ccol) for ccol in self.ccols]
            old_key = str(old_row)

            new_row = [new_value.__getattribute__(ccol) for ccol in self.ccols]
            new_key = str(new_row)

            # Drop old value
            utable = self.value
            self.uniques[old_key] -= 1
            if self.uniques[old_key] == 0:
                del self.uniques[old_key]
                for i, row in enumerate(utable):
                    if str(row) == old_key:
                        del utable[i]

            if self.uniques.get(new_key) is not None:
                self.uniques[new_key] += 1
                return
            self.uniques[new_key] = 1
            utable.append(new_row)

            self._on_updated()
            return
        raise TypeError(f"Expected type is SourceNode but real type is {type(new_value)}")


class CreateUtableNode(Command):
    source_id: UUID
    ccols: list[Ccol]
    uuid: UUID = Field(default_factory=uuid4)
