from abc import abstractmethod
from collections import deque

from loguru import logger

from src.pubsub import domain
from src.pubsub.repository import GraphRepoFake


class BaseHandler:
    def __init__(self, repo=GraphRepoFake()):
        self._repo = repo
        self._events: deque[domain.Event] = deque()
        self._commands: deque[domain.Command] = deque()

    def extend_commands(self, cmds: list[domain.Command]):
        self._commands.extend(cmds)

    def parse_commands(self) -> deque[domain.Command]:
        cmds = self._commands
        self._commands = deque()
        return cmds


class CommandHandler(BaseHandler):
    @abstractmethod
    def execute(self, cmd: domain.Command) -> domain.Pubsub:
        raise NotImplemented


class EventHandler(BaseHandler):
    @abstractmethod
    def handle(self, event: domain.Event):
        raise NotImplemented


class NodeSubscribedHandler(EventHandler):
    def handle(self, event: domain.NodeSubscribed):
        self._repo.append_node_parents(event.sub, event.pubs)
        for pub in event.pubs:
            self._repo.append_node_children(pub, {event.sub})


COMMON_EVENT_HANDLERS = {
    domain.NodeSubscribed: NodeSubscribedHandler,
}
