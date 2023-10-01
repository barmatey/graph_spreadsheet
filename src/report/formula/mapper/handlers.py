from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as mapper_domain


class MapperCreatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperCreated):
        logger.debug(f"MapperCreated.handle()")
        self._repo.add(event.entity)


class MapperUpdatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperUpdated):
        logger.debug("MapperUpdated.handle()")
        self._repo.update(event.new_value)


MAPPER_COMMAND_HANDLERS = {
}

MAPPER_EVENT_HANDlERS = {
    mapper_domain.MapperCreated: MapperCreatedHandler,
    mapper_domain.MapperUpdated: MapperUpdatedHandler,
}
