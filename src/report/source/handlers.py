from loguru import logger

from src.pubsub.handlers import CommandHandler, EventHandler
from src.report.wire import domain as wire_domain
from . import domain as source_domain


class CreateSourceHandler(CommandHandler):
    def execute(self, cmd: source_domain.CreateSource) -> source_domain.Source:
        source_node = source_domain.Source(uuid=cmd.uuid, title=cmd.title)
        return source_node


class SourceCreatedHandler(EventHandler):
    def handle(self, event: source_domain.SourceCreated):
        self._repo.add(event.entity)


class SourceDeletedHandler(EventHandler):
    def handle(self, event: source_domain.SourceDeleted):
        raise NotImplemented


class WireAppendedHandler(EventHandler):
    def handle(self, event: source_domain.WiresAppended):
        subs: set[source_domain.SourceSubscriber] = self._repo.get_node_children(event.source_node)
        for sub in subs:
            sub.on_wires_appended(event.wire_nodes)


class WireUpdatedHandler(EventHandler):
    def handle(self, event: source_domain.WireUpdated):
        subs: set[source_domain.SourceSubscriber] = self._repo.get_node_children(event.source)
        for sub in subs:
            sub.on_wire_updated(event.old_value, event.new_value)


SOURCE_COMMAND_HANDLERS = {
    source_domain.CreateSource: CreateSourceHandler,
}

SOURCE_EVENT_HANDLERS = {
    source_domain.SourceCreated: SourceCreatedHandler,
    source_domain.WiresAppended: WireAppendedHandler,
    source_domain.WireUpdated: WireUpdatedHandler,
}
