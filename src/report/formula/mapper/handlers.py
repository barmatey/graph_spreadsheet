from loguru import logger

from src.node.handlers import EventHandler
from . import domain as mapper_domain


class MapperUpdatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperUpdated):
        logger.debug("MapperUpdated.handle()")
        self._repo.update(event.new_value)


MAPPER_COMMAND_HANDLERS = {
}

MAPPER_EVENT_HANDlERS = {
    mapper_domain.MapperUpdated: MapperUpdatedHandler,
}
