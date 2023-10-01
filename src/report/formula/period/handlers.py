from loguru import logger

from src.pubsub.handlers import EventHandler

from . import domain as period_domain


class PeriodCreatedHandler(EventHandler):
    def handle(self, event: period_domain.PeriodCreated):
        logger.debug("PeriodCreated.handle()")
        self._repo.add(event.entity)


PERIOD_EVENT_HANDLERS = {
    period_domain.PeriodCreated: PeriodCreatedHandler,
}
