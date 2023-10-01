from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as cell_domain


class SheetCellCreatedHandler(EventHandler):
    def handle(self, event: cell_domain.SheetCellCreated):
        # logger.debug(f"SheetCellCreated.handle()")
        self._repo.add(event.entity)


class SheetCellUpdatedHandler(EventHandler):
    def handle(self, event: cell_domain.CellUpdated):
        self._repo.update(event.new_value)
        subs: set[cell_domain.CellSubscriber] = self._repo.get_node_children(event.new_value)
        logger.debug(f"CellUpdated.handle() => notify: {subs}")
        for sub in subs:
            sub.on_updated_cell(event.old_value, event.new_value)
            self.extend_events(sub.pase_events())


CELL_EVENT_HANDLERS = {
    cell_domain.SheetCellCreated: SheetCellCreatedHandler,
    cell_domain.CellUpdated: SheetCellUpdatedHandler,
}
