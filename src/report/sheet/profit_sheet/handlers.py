from uuid import UUID

from loguru import logger
import pandas as pd

from src.pubsub.handlers import CommandHandler, EventHandler
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.period import domain as period_domain
from ..group_sheet import domain as group_domain
from src.report.source import domain as source_domain
from . import domain as pf_domain


class CreateProfitSheetNodeHandler(CommandHandler):
    def __create_mappers(self, group_id: UUID, group_sheet) -> list[mapper_domain.Mapper]:
        mappers = []
        for i in range(0, group_sheet.size[0]):
            mapper = mapper_domain.Mapper(ccols=group_sheet.plan_items.ccols)
            pubs = set()
            for j in range(group_sheet.size[1]):
                cell = group_sheet.table[i][j]
                pubs.add(cell)
            mapper.follow_cell_publishers(pubs)
            self.extend_events(mapper.parse_events())
            self._repo.add(mapper)
            mappers.append(mapper)
        return mappers

    def __create_periods(self, start_date, end_date, period, freq) -> list[period_domain.Period]:
        date_range = [x.to_pydatetime() for x in pd.date_range(start_date, end_date, freq=f"{period}{freq}")]
        periods = []
        for start, end in zip(date_range[:-1], date_range[1:]):
            period = period_domain.Period(from_date=start, to_date=end)
            self._repo.add(period)
            self.extend_events(period.parse_events())
            periods.append(period)
        return periods

    def execute(self, cmd: pf_domain.CreateProfitSheet) -> pf_domain.ProfitSheet:
        logger.info(f"CreateProfitSheetNode.execute()")

        # Parent data
        group_sheet: group_domain.GroupSheet = self._repo.get_by_id(cmd.group_id)
        source = self._repo.get_by_id(cmd.source_id)
        mappers = self.__create_mappers(group_id=cmd.group_id, group_sheet=group_sheet)
        periods = self.__create_periods(cmd.start_date, cmd.end_date, cmd.period, cmd.freq)

        # Result sheet
        sheet_meta = pf_domain.ProfitSheetMeta(ccols=group_sheet.plan_items.ccols, periods=periods,
                                               source_id=cmd.source_id)
        profit_sheet = pf_domain.ProfitSheet(uuid=cmd.uuid, meta=sheet_meta)
        self._repo.add(profit_sheet)

        # Sheet subscribing
        profit_sheet.follow_sheet(group_sheet)

        left_indexes_len = len(mappers[0].ccols)
        # Create first row (no calculating, follow value only)
        row = []
        for j in range(0, left_indexes_len):
            cell = pf_domain.ProfitPeriodCell(index=(0, j), value=None)
            self._repo.add(cell)
            row.append(cell)

        for j, period in enumerate(periods, start=left_indexes_len):
            profit_cell = pf_domain.ProfitPeriodCell(index=(0, j), value=0)
            profit_cell.follow_periods({period})
            self.extend_events(profit_cell.parse_events())
            self._repo.add(profit_cell)
            row.append(profit_cell)
        profit_sheet.append_rows(row)

        # mapper is a row filter, period is a col filter
        rows = []
        for i, mapper in enumerate(mappers, start=1):
            row = []
            for j in range(0, left_indexes_len):
                cell = pf_domain.ProfitMapperCell(index=(i, j), value=None)
                cell.follow_mappers({mapper})
                self._repo.add(cell)
                self.extend_events(cell.parse_events())
                row.append(cell)

            for j, period in enumerate(periods, start=left_indexes_len):
                profit_cell = pf_domain.ProfitCell(index=(i, j), value=0)
                profit_cell.follow_periods({period})
                profit_cell.follow_mappers({mapper})
                profit_cell.follow_source(source)
                self._repo.add(profit_cell)
                self.extend_events(profit_cell.parse_events())
                row.append(profit_cell)
            rows.append(row)
        profit_sheet.append_rows(rows)
        self.extend_events(profit_sheet.parse_events())

        return profit_sheet


class GroupSheetRowsAppendedHandler(EventHandler):
    def handle(self, event: pf_domain.GroupSheetRowsAppended):
        logger.debug(f"GroupSheetRowsAppended.handle()")
        sheet = event.profit_sheet
        source: source_domain.Source = self._repo.get_by_id(sheet.meta.source_id)

        to_append = []
        for i, index_row in enumerate(event.rows, start=sheet.size[0]):
            row = []
            mapper = mapper_domain.Mapper(ccols=sheet.meta.ccols)
            mapper.follow_cell_publishers(index_row)
            self.extend_events(mapper.parse_events())
            self._repo.add(mapper)
            for cell in index_row:
                index_cell = pf_domain.ProfitMapperCell(index=cell.index, value=cell.value)
                index_cell.follow_cell_publishers({cell})
                row.append(cell)
                self.extend_events(index_cell.parse_events())
                self._repo.add(index_cell)
            for j, period in enumerate(sheet.meta.periods, start=len(sheet.meta.ccols)):
                cell = pf_domain.ProfitCell(index=(i, j), value=0)
                cell.follow_mappers({mapper})
                cell.follow_periods({period})
                cell.follow_source(source)
                row.append(cell)
                self._repo.add(cell)
                self.extend_events(cell.parse_events())
            to_append.append(row)

        sheet.append_rows(to_append)
        self.extend_events(sheet.parse_events())


class ProfitCellRecalculateRequestedHandler(EventHandler):
    def handle(self, event: pf_domain.ProfitCellRecalculateRequested):
        profit_cell = event.node
        source: source_domain.Source = filter(
            lambda x: isinstance(x, source_domain.Source),
            self._repo.get_node_parents(profit_cell)
        ).__next__()
        profit_cell.recalculate(source.wires)
        self.extend_events(profit_cell.parse_events())
        logger.debug(f"ProfitCellRecalculateRequested.handle()")


PROFIT_SHEET_COMMAND_HANDLERS = {
    pf_domain.CreateProfitSheet: CreateProfitSheetNodeHandler,
}

PROFIT_SHEET_EVENT_HANDLERS = {
    pf_domain.GroupSheetRowsAppended: GroupSheetRowsAppendedHandler,
}

PROFIT_CELL_EVENT_HANDLERS = {
    pf_domain.ProfitCellRecalculateRequested: ProfitCellRecalculateRequestedHandler,
}

PROFIT_CELL_COMMAND_HANDLERS = {
}
