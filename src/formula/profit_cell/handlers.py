from loguru import logger

from src.node.handlers import CommandHandler, EventHandler
from src.wire import domain as wire_domain
from . import domain as pf_domain


class CreateProfitCellNodeHandler(CommandHandler):
    def execute(self, cmd: pf_domain.CreateProfitCellNode) -> pf_domain.ProfitCellNode:
        logger.error(f"CreateProfitSumNode.execute()")
        mapper = self._repo.get_by_id(cmd.mapper_node_id)
        source = self._repo.get_by_id(cmd.source_node_id)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))
        profit_cell_node = pf_domain.ProfitCellNode(value=0)
        self._repo.add(profit_cell_node)

        # Subscribing
        profit_cell_node.follow({mapper})
        self.extend_events(profit_cell_node.parse_events()[1:2])
        profit_cell_node.follow(wires)
        self.extend_events(profit_cell_node.parse_events())
        return profit_cell_node


class ProfitCellMapperUpdatedHandler(EventHandler):
    def handle(self, event: pf_domain.ProfitCellMapperUpdated):
        profit_cell = event.node
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(profit_cell)))
        profit_cell.recalculate(wires)
        self.extend_events(profit_cell.parse_events())
        logger.debug(f"ProfitCellMapperUpdatedHandler")


PROFIT_CELL_EVENT_HANDLERS = {
    pf_domain.ProfitCellMapperUpdated: ProfitCellMapperUpdatedHandler,
}

PROFIT_CELL_COMMAND_HANDLERS = {
    pf_domain.CreateProfitCellNode: CreateProfitCellNodeHandler,
}
