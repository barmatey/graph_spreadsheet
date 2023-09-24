from loguru import logger

from src.node.handlers import CommandHandler
from . import domain as period_domain


class CreatePeriodNodeHandler(CommandHandler):
    def execute(self, cmd: period_domain.CreatePeriodNode) -> period_domain.PeriodNode:
        logger.info(f"CreatePeriodNode.execute()")
        node = period_domain.PeriodNode(from_date=cmd.from_date, to_date=cmd.to_date)
        self._repo.add(node)
        return node


PERIOD_COMMAND_HANDLERS = {
    period_domain.CreatePeriodNode: period_domain.CreatePeriodNode,
}
