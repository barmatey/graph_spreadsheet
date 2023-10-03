from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as sindex_domain


class SindexCreatedHandler(EventHandler):
    def handle(self, event: sindex_domain.SindexCreated):
        self._repo.add(event.entity)


class SindexDeletedHandler(EventHandler):
    def handle(self, event: sindex_domain.SindexDeleted):
        self._repo.remove(event.entity)


SINDEX_EVENT_HANDLERS = {
    sindex_domain.SindexCreated: SindexCreatedHandler,
    sindex_domain.SindexDeleted: SindexDeletedHandler,
}
