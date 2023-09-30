from loguru import logger

from src.pubsub.handlers import CommandHandler, EventHandler
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
        source = self._repo.get_by_id(event.profit_sheet.meta.source_id)
        profit_sheet = event.profit_sheet
        profit_sheet = pf_usecases.AppendRowsUsecase(profit_sheet, event.rows, event.cells, source).execute()
        self.extend_events(profit_sheet.parse_events(deep=True))


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
