from loguru import logger

from src.node.handlers import CommandHandler, EventHandler
from src.report.wire import domain as wire_domain
from . import domain as pf_domain


class CreateProfitCellNodeHandler(CommandHandler):
    def execute(self, cmd: pf_domain.CreateProfitCellNode) -> pf_domain.ProfitCellNode:
        logger.error(f"CreateProfitSumNode.execute()")

        # Get parents
        mapper = self._repo.get_by_id(cmd.mapper_node_id)
        period = self._repo.get_by_id(cmd.period_node_id)
        source = self._repo.get_by_id(cmd.source_node_id)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))

        # Create node
        profit_cell_node = pf_domain.ProfitCellNode(value=0)
        self._repo.add(profit_cell_node)

        # Subscribing
        profit_cell_node.follow({mapper, period})
        self.extend_events(profit_cell_node.parse_events())
        profit_cell_node.follow(wires)
        self.extend_events(profit_cell_node.parse_events())
        return profit_cell_node


class ProfitCellRecalculateRequestedHandler(EventHandler):
    def handle(self, event: pf_domain.ProfitCellRecalculateRequested):
        profit_cell = event.node
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(profit_cell)))
        profit_cell.recalculate(wires)
        self.extend_events(profit_cell.parse_events())
        logger.debug(f"ProfitCellRecalculateRequested.handle()")


PROFIT_CELL_EVENT_HANDLERS = {
    pf_domain.ProfitCellRecalculateRequested: ProfitCellRecalculateRequestedHandler,
}

PROFIT_CELL_COMMAND_HANDLERS = {
    pf_domain.CreateProfitCellNode: CreateProfitCellNodeHandler,
}
