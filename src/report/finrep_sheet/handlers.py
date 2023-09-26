from loguru import logger
import pandas as pd

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.period import domain as period_domain
from src.report.formula.profit_cell import domain as pf_domain
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
        mappers = []
        for i in range(0, group_sheet.size[0]):
            mapper = mapper_domain.MapperNode(ccols=group_sheet.plan_items.ccols)
            self._repo.add(mapper)
            pubs = set()
            for j in range(group_sheet.size[1]):
                cell = group_sheet.table[i][j]
                pubs.add(cell)
            mapper.follow(pubs)
            self.extend_events(mapper.parse_events())
            mappers.append(mapper)

        # Create periods:
        date_range = pd.date_range(cmd.start_date, cmd.end_date, freq=f"{cmd.period}{cmd.freq}")
        periods = [period_domain.PeriodNode(from_date=start, to_date=end)
                   for start, end in zip(date_range[:-1], date_range[1:])]

        # Create sheet
        table = []
        row = []
        for j, period in enumerate(periods):
            sheet_cell = cell_domain.CellNode(index=(0, j), value=str(period.to_date))
            row.append(sheet_cell.value)
        table.append(row)

        for i, mapper in enumerate(mappers):
            row = []
            for j, period in enumerate(periods):
                profit_cell = pf_domain.ProfitCellNode(value=0)
                profit_cell.follow({mapper, period})
                profit_cell.follow(wires)

                sheet_cell = cell_domain.CellNode(index=(i, j + 1), value=None)
                sheet_cell.follow({profit_cell})

                row.append(sheet_cell.value)
            table.append(row)

        for row in table:
            logger.success(row)

        return profit_sheet


FINREP_COMMAND_HANDLERS = {
    finrep_domain.CreateProfitSheetNode: CreateProfitSheetNodeHandler,
}
