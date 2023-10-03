from loguru import logger

from src.pubsub.handlers import EventHandler
from src.spreadsheet.sheet import domain as sheet_domain
from src.spreadsheet.sindex import domain as sindex_domain


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


class RowsDeletedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsDeleted):
        linked_rows: set[sindex_domain.Sindex] = set()
        for deleted_row in event.deleted_rows:
            linked_rows.union(self._repo.get_node_children(deleted_row))


class RowsReindexedHandler(EventHandler):
    def handle(self, event: sheet_domain.SheetReindexed):
        pass


SHEET_EVENT_HANDLERS = {
    sheet_domain.SheetCreated: SheetCreatedHandler,
    sheet_domain.RowsAppended: RowsAppendedHandler,
    sheet_domain.RowsDeleted:  RowsDeletedHandler,
    sheet_domain.SheetReindexed: RowsReindexedHandler,
}
