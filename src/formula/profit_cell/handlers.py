from loguru import logger

from src.node.handlers import CommandHandler
from src.wire import domain as wire_domain
from . import domain as pf_domain


class CreateProfitCellNodeHandler(CommandHandler):
    def execute(self, cmd: pf_domain.CreateProfitCellNode) -> pf_domain.ProfitCellNode:
        logger.error(f"CreateProfitSumNode.execute()")
        mapper = self._repo.get_by_id(cmd.mapper_node_id)
        profit_cell_node = pf_domain.ProfitCellNode(sum=0)
        self._repo.add(profit_cell_node)
        profit_cell_node.follow({mapper})
        self.extend_events(profit_cell_node.parse_events())
        return profit_cell_node


PROFIT_CELL_COMMAND_HANDLERS = {
    pf_domain.CreateProfitCellNode: CreateProfitCellNodeHandler,
}
