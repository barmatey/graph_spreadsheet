from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as sindex_domain


class SindexCreatedHandler(EventHandler):
    def handle(self, event: sindex_domain.SindexCreated):
        # logger.debug(f"sindex_domainCreated.handle()")
        self._repo.add(event.entity)


class SindexDeletedHandler(EventHandler):
    def handle(self, event: sindex_domain.SindexDeleted):
        subs: set[sindex_domain.SindexSubscriber] = self._repo.get_node_children(event.entity)
        logger.debug(f"SindexDeleted.handle() => notify: {subs}")
        for sub in subs:
            sub.on_sindex_deleted(event.entity)

        self._repo.remove(event.entity)



SINDEX_EVENT_HANDLERS = {
    sindex_domain.SindexCreated: SindexCreatedHandler,
}
