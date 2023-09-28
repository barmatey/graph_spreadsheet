from loguru import logger

from src.node.handlers import EventHandler
from . import domain as sheet_domain


class RowAppendedHandler(EventHandler):
    def handle(self, event: sheet_domain.RowAppended):
        logger.debug(f"RowAppended.handle()")
        for cell in event.row:
            self._repo.add(cell)
        self._repo.update(event.sheet)


SHEET_EVENT_HANDLERS = {
    sheet_domain.RowAppended: RowAppendedHandler,
}
