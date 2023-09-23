from abc import abstractmethod
from collections import deque

from loguru import logger

from src.node import domain
from src.node.repository import GraphRepoFake


class BaseHandler:
    def __init__(self, repo=GraphRepoFake()):
        self._repo = repo
        self._events: deque[domain.Event] = deque()
        self._commands: deque[domain.Command] = deque()

    def extend_events(self, events: list[domain.Event]):
        self._events.extend(events)

    def extend_commands(self, cmds: list[domain.Command]):
        self._commands.extend(cmds)

    def parse_events(self) -> deque[domain.Event]:
        events = self._events
        self._events = deque()
        return events

    def parse_commands(self) -> deque[domain.Command]:
        cmds = self._commands
        self._commands = deque()
        return cmds


class CommandHandler(BaseHandler):
    @abstractmethod
    def execute(self, cmd: domain.Command) -> domain.Node:
        raise NotImplemented


class EventHandler(BaseHandler):
    @abstractmethod
    def handle(self, event: domain.Event):
        raise NotImplemented


class NodeUpdatedHandler(EventHandler):
    def handle(self, event: domain.NodeUpdated):
        # Save
        self._repo.update(event.new_value)

        # Update subscribers
        subs = self._repo.get_node_children(event.new_value.uuid)
        for sub in subs:
            sub.on_pub_updated(event.old_value, event.new_value)
            self.extend_events(sub.parse_events())

        logger.debug(f"{event.new_value.__class__.__name__}UpdatedHandler => update: {subs}")


COMMON_EVENT_HANDLERS = {
    domain.NodeUpdated: NodeUpdatedHandler,
}
