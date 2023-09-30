from loguru import logger

from src.pubsub.handlers import EventHandler
from . import domain as sindex_domain


class SindexCreatedHandler(EventHandler):
    def handle(self, event: sindex_domain.SindexCreated):
        logger.debug(f"sindex_domainCreated.handle()")
        self._repo.add(event.entity)
