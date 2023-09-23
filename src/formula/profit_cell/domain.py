from uuid import UUID, uuid4

from loguru import logger
from pydantic import Field

from src.node.domain import Node, Command, Event
from src.formula.mapper import domain as mapper_domain
from src.wire import domain as wire_domain


class ProfitCellNode(Node):
    sum: float
    mapper: mapper_domain.MapperNode | None = None
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)

    def follow(self, pubs: set['Node']):
        for pub in pubs:
            if isinstance(pub, wire_domain.WireNode):
                logger.warning(f"on_subscribe, is_filtred={self.value.report_filter.is_filtred(pub)}")
                if self.mapper.is_filtred(pub):
                    self.sum += pub.amount
            elif isinstance(pub, mapper_domain.MapperNode):
                self.mapper = pub
            else:
                raise TypeError(f"real type is {type(pub)}")
        self._on_subscribed(pubs)
        self._on_updated()

    def update(self, old_value: 'Node', new_value: 'Node'):
        if isinstance(old_value, wire_domain.WireNode) and isinstance(new_value, wire_domain.WireNode):
            self.value.sum -= old_value.amount
            if self._report_filter.is_filtred(new_value):
                self.value.sum += new_value.value.amount
            return
        if isinstance(new_value, mapper_domain.MapperNode):
            self.events.append(ProfitCellMapperUpdated(node=self))
            return
        raise TypeError(f"real type is {type(old_value)}, {type(new_value)}")


class CreateProfitCellNode(Command):
    mapper_node_id: UUID
    source_node_id: UUID
    uuid: UUID = Field(default_factory=uuid4)


class ProfitCellMapperUpdated(Event):
    node: ProfitCellNode
    uuid: UUID = Field(default_factory=uuid4)
