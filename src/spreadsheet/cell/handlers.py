from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as cell_domain


class CellCreatedHandler(EventHandler):
    def handle(self, event: cell_domain.CellCreated):
        self._repo.add(event.entity)


class CellDeletedHandler(EventHandler):
    def handle(self, event: cell_domain.CellDeleted):
        _ = self._repo.get_by_id(event.entity.uuid)
        logger.success(f"DELETING CELL EXIST YET")
        subs: set[cell_domain.CellSubscriber] = self._repo.get_node_children(event.entity)
        for sub in subs:
            sub.on_cell_deleted(event.entity)

        self._repo.remove(event.entity)


class SheetCellUpdatedHandler(EventHandler):
    def handle(self, event: cell_domain.CellUpdated):
        self._repo.update(event.new_value)
        subs: set[cell_domain.CellSubscriber] = self._repo.get_node_children(event.new_value)
        for sub in subs:
            sub.on_cell_updated(event.old_value, event.new_value)


CELL_EVENT_HANDLERS = {
    cell_domain.CellCreated: CellCreatedHandler,
    cell_domain.CellDeleted: CellDeletedHandler,
    cell_domain.CellUpdated: SheetCellUpdatedHandler,
}
