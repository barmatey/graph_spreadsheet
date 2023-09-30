from loguru import logger

from src.pubsub.handlers import EventHandler
from src.spreadsheet.sheet import domain as sheet_domain


class RowsAppendedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsAppended):
        # Save
        self._repo.update(event.sheet)
        for row in event.rows:
            for cell in row:
                self._repo.add(cell)

        # Notify
        subs: set[sheet_domain.SheetSubscriber] = self._repo.get_node_children(event.sheet)
        logger.debug(f"RowsAppended.handle() => notify: {subs}")
        for sub in subs:
            sub.on_rows_appended(event.rows)
            self.extend_events(sub.parse_events())


class RowsDeletedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsDeleted):
        logger.warning("RowsDeleted.handle()")
        pass


class RowsReindexedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsReindexed):
        logger.debug("RowsReindexed.handle()")
        for i in range(0, event.sheet.size[0]):
            for j in range(0, event.sheet.size[1]):
                self._repo.update(event.sheet.table[i][j])


SHEET_EVENT_HANDLERS = {
    sheet_domain.RowsAppended: RowsAppendedHandler,
    sheet_domain.RowsDeleted: RowsDeletedHandler,
    sheet_domain.RowsReindexed: RowsReindexedHandler,
}
