from uuid import UUID

from loguru import logger
import pandas as pd

import src.report
import src.report.finrep_sheet.domain
from src.node.handlers import CommandHandler, EventHandler
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.period import domain as period_domain
from src.report.group_sheet import domain as group_domain
from . import domain as finrep_domain
from ..source import domain as source_domain


class CreateProfitSheetNodeHandler(CommandHandler):

    def __create_mappers(self, group_id: UUID) -> list[mapper_domain.MapperNode]:
        group_sheet: group_domain.GroupSheetNode = self._repo.get_by_id(group_id)
        mappers = []
        for i in range(0, group_sheet.size[0]):
            mapper = mapper_domain.MapperNode(ccols=group_sheet.plan_items.ccols)
            pubs = set()
            for j in range(group_sheet.size[1]):
                cell = group_sheet.table[i][j]
                pubs.add(cell)
            mapper.follow_cell_publishers(pubs)
            self.extend_events(mapper.parse_events())
            self._repo.add(mapper)
            mappers.append(mapper)
        return mappers

    def __create_periods(self, start_date, end_date, period, freq) -> list[period_domain.PeriodNode]:
        date_range = [x.to_pydatetime() for x in pd.date_range(start_date, end_date, freq=f"{period}{freq}")]
        periods = []
        for start, end in zip(date_range[:-1], date_range[1:]):
            period = period_domain.PeriodNode(from_date=start, to_date=end)
            self._repo.add(period)
            self.extend_events(period.parse_events())
            periods.append(period)
        return periods

    def execute(self, cmd: finrep_domain.CreateProfitSheetNode) -> finrep_domain.FinrepSheet:
        logger.info(f"CreateProfitSheetNode.execute()")

        # Result sheet
        profit_sheet = finrep_domain.FinrepSheet(uuid=cmd.uuid)
        self._repo.add(profit_sheet)

        # Parent data
        source = self._repo.get_by_id(cmd.source_id)
        mappers = self.__create_mappers(group_id=cmd.group_id)
        periods = self.__create_periods(cmd.start_date, cmd.end_date, cmd.period, cmd.freq)

        # Create first row (no calculating, follow value only)
        rows = []
        for j, period in enumerate(periods):
            profit_cell = src.report.finrep_sheet.domain.ProfitPeriodCell(index=(0, j), value=0)
            profit_cell.follow_periods({period})
            self.extend_events(profit_cell.parse_events())
            self._repo.add(profit_cell)
            rows.append(profit_cell)
        profit_sheet.append_rows(rows)

        # mapper is a row filter, period is a col filter
        rows = []
        for i, mapper in enumerate(mappers):
            row = []
            for j, period in enumerate(periods):
                profit_cell = src.report.finrep_sheet.domain.ProfitCell(index=(i, j + 1), value=0)
                profit_cell.follow_periods({period})
                profit_cell.follow_mappers({mapper})
                profit_cell.follow_source(source)
                self._repo.add(profit_cell)
                self.extend_events(profit_cell.parse_events())
                row.append(profit_cell)
            rows.append(row)
        profit_sheet.append_rows(rows)

        return profit_sheet


FINREP_COMMAND_HANDLERS = {
    finrep_domain.CreateProfitSheetNode: CreateProfitSheetNodeHandler,
}


class CreateProfitCellNodeHandler(CommandHandler):
    def execute(self, cmd: src.report.finrep_sheet.domain.CreateProfitCellNode) -> src.report.finrep_sheet.domain.ProfitCell:
        logger.error(f"CreateProfitSumNode.execute()")

        # Get parents
        mapper = self._repo.get_by_id(cmd.mapper_node_id)
        period = self._repo.get_by_id(cmd.period_node_id)
        source = self._repo.get_by_id(cmd.source_node_id)

        # Create node
        profit_cell_node = src.report.finrep_sheet.domain.ProfitCell(value=0)
        self._repo.add(profit_cell_node)

        # Subscribing
        profit_cell_node.follow({mapper, period})
        self.extend_events(profit_cell_node.parse_events())
        profit_cell_node.follow({source})
        self.extend_events(profit_cell_node.parse_events())
        return profit_cell_node


class ProfitCellRecalculateRequestedHandler(EventHandler):
    def handle(self, event: src.report.finrep_sheet.domain.ProfitCellRecalculateRequested):
        profit_cell = event.node
        source: source_domain.Source = filter(
            lambda x: isinstance(x, source_domain.Source),
            self._repo.get_node_parents(profit_cell)
        ).__next__()
        profit_cell.recalculate(source.wires)
        self.extend_events(profit_cell.parse_events())
        logger.debug(f"ProfitCellRecalculateRequested.handle()")


PROFIT_CELL_EVENT_HANDLERS = {
    src.report.finrep_sheet.domain.ProfitCellRecalculateRequested: ProfitCellRecalculateRequestedHandler,
}
PROFIT_CELL_COMMAND_HANDLERS = {
    src.report.finrep_sheet.domain.CreateProfitCellNode: CreateProfitCellNodeHandler,
}
