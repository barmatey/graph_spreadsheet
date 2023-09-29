from loguru import logger

from src.node.handlers import CommandHandler, EventHandler
from . import domain as source_domain


class CreateSourceNodeHandler(CommandHandler):
    def execute(self, cmd: source_domain.CreateSourceNode) -> source_domain.Source:
        logger.info("CreateSourceNode.execute()")
        source_node = source_domain.Source(uuid=cmd.uuid, title=cmd.title)
        self._repo.add(source_node)
        return source_node


class WireAppendedHandler(EventHandler):
    def handle(self, event: source_domain.WireNodesAppended):
        subs: set[source_domain.SourceSubscriber] = self._repo.get_node_children(event.source_node)
        logger.debug(f"SourceWiresAppended.handle() => notify: {subs}")
        for sub in subs:
            sub.on_wires_appended(event.wire_nodes)
            self.extend_events(sub.parse_events())


class WireUpdatedHandler(EventHandler):
    def handle(self, event: source_domain.WireUpdated):
        subs: set[source_domain.SourceSubscriber] = self._repo.get_node_children(event.source)
        logger.debug(f"SourceWireUpdated.handle() =>  notify: f{subs}")
        for sub in subs:
            sub.on_wire_updated(event.old_value, event.new_value)
            self.extend_events(sub.parse_events())


SOURCE_COMMAND_HANDLERS = {
    source_domain.CreateSourceNode: CreateSourceNodeHandler,
}

SOURCE_EVENT_HANDLERS = {
    source_domain.WireNodesAppended: WireAppendedHandler,
    source_domain.WireUpdated: WireUpdatedHandler,
}
