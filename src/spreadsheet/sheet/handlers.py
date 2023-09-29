from loguru import logger

from src.node.handlers import EventHandler
from . import domain as sheet_domain


class RowsAppendedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsAppended):
        logger.debug(f"RowsAppended.handle()")
        for row in event.rows:
            for cell in row:
                self._repo.add(cell)
        self._repo.update(event.sheet)


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
