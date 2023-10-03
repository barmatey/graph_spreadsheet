from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as mapper_domain


class MapperCreatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperCreated):
        self._repo.add(event.entity)


class MapperUpdatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperUpdated):
        self._repo.update(event.new_value)


class ParentCellDeletedHandler(EventHandler):
    def handle(self, event: mapper_domain.ParentCellDeleted):
        subs: set[mapper_domain.MapperSubscriber] = self._repo.get_node_children(event.entity)
        for sub in subs:
            sub.on_mapper_deleted(event.entity)

        self._repo.remove(event.entity)


MAPPER_COMMAND_HANDLERS = {
}

MAPPER_EVENT_HANDlERS = {
    mapper_domain.MapperCreated: MapperCreatedHandler,
    mapper_domain.MapperUpdated: MapperUpdatedHandler,
    mapper_domain.ParentCellDeleted: ParentCellDeletedHandler,
}
