from src.node.handlers import EventHandler
from . import domain as cell_domain


class CellUpdatedHandler(EventHandler):
    def handle(self, event: cell_domain.CellUpdated):
        self._repo.update(event.new_value)


CELL_EVENT_HANDLERS = {
    cell_domain.CellUpdated: CellUpdatedHandler,
}
