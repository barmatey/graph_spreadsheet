from uuid import UUID

from loguru import logger
import pandas as pd

from src.node.handlers import CommandHandler
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.period import domain as period_domain
from src.report.formula.profit_cell import domain as pf_domain
from src.report.group_sheet import domain as group_domain
from src.spreadsheet.cell import domain as cell_domain
from . import domain as finrep_domain


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
        profit_sheet = finrep_domain.FinrepSheet()
        self._repo.add(profit_sheet)

        # Parent data
        source = self._repo.get_by_id(cmd.source_id)
        mappers = self.__create_mappers(group_id=cmd.group_id)
        periods = self.__create_periods(cmd.start_date, cmd.end_date, cmd.period, cmd.freq)

        # Create first row (no calculating, follow value only)
        rows = []
        for j, period in enumerate(periods):
            sheet_cell = cell_domain.SheetCell(index=(0, j), value=None)
            sheet_cell.follow_cell_publishers({period})
            self.extend_events(sheet_cell.parse_events())
            self._repo.add(sheet_cell)
            rows.append(sheet_cell)
        profit_sheet.append_rows(rows)

        # mapper is a row filter, period is a col filter
        for i, mapper in enumerate(mappers):
            row = []
            for j, period in enumerate(periods):
                profit_cell = pf_domain.ProfitCellNode(value=0)
                profit_cell.follow_cell_publishers({mapper, period})
                profit_cell.follow_source(source)
                profit_cell.as_child({profit_sheet})
                self._repo.add(profit_cell)
                self.extend_events(profit_cell.parse_events())

                sheet_cell = cell_domain.Cell(index=(i, j + 1), value=None)
                sheet_cell.follow({profit_cell})
                self._repo.add(sheet_cell)
                self.extend_events(sheet_cell.parse_events())
                row.append(sheet_cell)
            profit_sheet.append_row(row)

        return profit_sheet


FINREP_COMMAND_HANDLERS = {
    finrep_domain.CreateProfitSheetNode: CreateProfitSheetNodeHandler,
}
