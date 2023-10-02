from loguru import logger

from src.pubsub.handlers import EventHandler
from src.spreadsheet.sheet import domain as sheet_domain


class SheetCreatedHandler(EventHandler):
    def handle(self, event: sheet_domain.SheetCreated):
        self._repo.add(event.entity)


class RowsAppendedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsAppended):
        # Save
        self._repo.update(event.sheet)

        # Notify
        subs: set[sheet_domain.SheetSubscriber] = self._repo.get_node_children(event.sheet)
        for sub in subs:
            sub.on_rows_appended(event.rows, event.cells)


class RowsReindexedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsReindexed):
        pass




SHEET_EVENT_HANDLERS = {
    sheet_domain.SheetCreated: SheetCreatedHandler,
    sheet_domain.RowsAppended: RowsAppendedHandler,
    sheet_domain.RowsReindexed: RowsReindexedHandler,
}
