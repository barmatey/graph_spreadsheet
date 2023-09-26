from loguru import logger

from src.node.handlers import CommandHandler, EventHandler
from . import domain as source_domain


class CreateSourceNodeHandler(CommandHandler):
    def execute(self, cmd: source_domain.CreateSourceNode) -> source_domain.SourceNode:
        logger.info("CreateSourceNode.execute()")
        source_node = source_domain.SourceNode(title=cmd.title)
        self._repo.add(source_node)
        return source_node


class WireNodesAppendedHandler(EventHandler):
    def handle(self, event: source_domain.WireNodesAppended):
        logger.debug("WireNodeAppended.handle()")
        subs = self._repo.get_node_children(event.source_node)
        for sub in subs:
            sub.follow(event.wire_nodes)
            self.extend_events(sub.parse_events())


SOURCE_COMMAND_HANDLERS = {
    source_domain.CreateSourceNode: CreateSourceNodeHandler,
}

SOURCE_EVENT_HANDLERS = {
    source_domain.WireNodesAppended: WireNodesAppendedHandler,
}
