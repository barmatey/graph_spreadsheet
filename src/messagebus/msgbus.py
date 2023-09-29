from collections import deque
from uuid import UUID

from loguru import logger

from .command_handlers import get_command_handler
from .event_handlers import get_event_handler
from ..helpers.decorators import singleton
from ..node.domain import Event, Pubsub, Command


@singleton
class Msgbus:
    def __init__(self):
        self._commands: deque[Command] = deque()
        self._events: deque[Event] = deque()
        self.results: dict[UUID, Pubsub] = {}

    def push_command(self, cmd: Command):
        self._commands.append(cmd)

    def push_event(self, event: Event):
        self._events.append(event)

    def run(self):
        while self._commands:
            cmd = self._commands.popleft()
            handler = get_command_handler(cmd)
            self.results[cmd.uuid] = handler.execute(cmd)
            self._events.extend(handler.parse_events())
            self._commands.extend(handler.parse_commands())

            while self._events:
                event = self._events.popleft()
                handler = get_event_handler(event)
                handler.handle(event)
                self._events.extend(handler.parse_events())
                self._commands.extend(handler.parse_commands())
