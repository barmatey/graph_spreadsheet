from uuid import UUID

from loguru import logger
import pandas as pd

from src.pubsub.handlers import CommandHandler, EventHandler
from src.report.formula.mapper import domain as mapper_domain
from src.spreadsheet.sindex.domain import Sindex
from src.report.source import domain as source_domain
from . import domain as pf_domain
from . import usecases as pf_usecases


class CreateProfitSheetNodeHandler(CommandHandler):
    def execute(self, cmd: pf_domain.CreateProfitSheet) -> pf_domain.ProfitSheet:
        logger.info(f"CreateProfitSheetNode.execute()")
        profit_sheet = pf_usecases.CreateProfitSheetUsecase(cmd, self._repo).execute()
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
                index_cell = pf_domain.ProfitMapperCell(row_index=cell.row_index, col_index=cell.col_index, value=cell.value)
                index_cell.follow_cell_publishers({cell})
                row.append(cell)
                self.extend_events(index_cell.parse_events())
                self._repo.add(index_cell)
            for j, period in enumerate(sheet.meta.periods, start=len(sheet.meta.ccols)):
                cell = pf_domain.ProfitCell(row_index=Sindex(position=i), col_index=Sindex(position=j), value=0)
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
