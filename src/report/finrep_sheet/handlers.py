from loguru import logger

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.report.formula.mapper import domain as mapper_domain
from src.report.group_sheet import domain as group_domain
from src.spreadsheet.cell import domain as cell_domain
from . import domain as finrep_domain


class CreateProfitSheetNodeHandler(CommandHandler):
    def execute(self, cmd: finrep_domain.CreateProfitSheetNode) -> finrep_domain.FinrepSheet:
        logger.info(f"CreateProfitSheetNode.execute()")
        # Get data
        source = self._repo.get_by_id(cmd.source_id)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))

        group_sheet: group_domain.GroupSheetNode = self._repo.get_by_id(cmd.group_id)
        cells = list(filter(lambda x: isinstance(x, cell_domain.CellNode), self._repo.get_node_children(group_sheet)))
        logger.success(cells)

        profit_sheet = finrep_domain.FinrepSheet()
        self._repo.add(profit_sheet)

        return profit_sheet


FINREP_COMMAND_HANDLERS = {
    finrep_domain.CreateProfitSheetNode: CreateProfitSheetNodeHandler,
}
