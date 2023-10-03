from collections import deque
from uuid import UUID

from loguru import logger

from .command_handlers import get_command_handler
from .event_handlers import get_event_handler
from ..helpers.decorators import singleton
from ..pubsub.domain import Event, Pubsub, Command, EventQueue


@singleton
class Msgbus:
    def __init__(self):
        self._commands: deque[Command] = deque()
        self._events: deque[Event] = deque()
        self._event_queue = EventQueue()
        self.results: dict[UUID, Pubsub] = {}

    def push_command(self, cmd: Command):
        self._commands.append(cmd)

    def push_event(self, event: Event):
        self._events.append(event)

    def _extend_events(self):
        for event in self._event_queue.parse_events():
            logger.debug(f"ADDED: {event}:{event.priority}")
            self._events.append(event)

    def run(self):
        while self._commands:
            cmd = self._commands.popleft()
            handler = get_command_handler(cmd)
            self.results[cmd.uuid] = handler.execute(cmd)
            self._extend_events()
            self._commands.extend(handler.parse_commands())

            while self._events:
                event = self._events.popleft()
                logger.debug(f"EXTRACTED: {event}:{event.priority}")
                handler = get_event_handler(event)
                try:
                    handler.handle(event)
                except Exception as err:
                    logger.error(f"EXCEPTION: {err}")
                    for e in self._events:
                        logger.error(e)
                    raise err
                self._extend_events()
                self._commands.extend(handler.parse_commands())
