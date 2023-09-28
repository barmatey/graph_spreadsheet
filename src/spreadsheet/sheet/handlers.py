from loguru import logger

from src.node.handlers import EventHandler
from . import domain as sheet_domain


class RowsAppendedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsAppended):
        logger.debug(f"RowAppended.handle()")
        for row in event.rows:
            for cell in row:
                self._repo.add(cell)
        self._repo.update(event.sheet)


class RowsDeletedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowsDeleted):
        logger.debug("RowsDeleted.handle()")
        for row in event.sheet.table:
            for cell in row:
                self._repo.update(cell)
        self._repo.update(event.sheet)


SHEET_EVENT_HANDLERS = {
    sheet_domain.RowsAppended: RowsAppendedHandler,
    sheet_domain.RowsDeleted: RowsDeletedHandler,
}
