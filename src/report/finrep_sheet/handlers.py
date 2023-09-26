from loguru import logger
from datetime import timedelta

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

        profit_sheet = finrep_domain.FinrepSheet()
        self._repo.add(profit_sheet)

        # Create mappers
        for i in range(0, group_sheet.size[0]):
            mapper = mapper_domain.MapperNode(ccols=group_sheet.plan_items.ccols)
            self._repo.add(mapper)
            pubs = set()
            for j in range(group_sheet.size[1]):
                cell = group_sheet.table[i][j]
                pubs.add(cell)
            mapper.follow(pubs)
            self.extend_events(mapper.parse_events())

        # Create periods:
        start = cmd.start_date
        end = start + timedelta(days=cmd.period_day, )

        return profit_sheet


FINREP_COMMAND_HANDLERS = {
    finrep_domain.CreateProfitSheetNode: CreateProfitSheetNodeHandler,
}
