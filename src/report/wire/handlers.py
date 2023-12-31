from loguru import logger

from src.pubsub.handlers import CommandHandler, EventHandler
from . import domain as wire_domain
from src.report.source import domain as source_domain


class CreateWireHandler(CommandHandler):
    def execute(self, cmd: wire_domain.CreateWire) -> wire_domain.Wire:
        logger.info("CreateWireNode.execute()")

        # Create wire node
        wire_node = wire_domain.Wire(**cmd.model_dump(exclude={"source_id"}))

        # Append wire to source
        source_node: source_domain.Source = self._repo.get_by_id(cmd.source_id)
        source_node.follow_wires({wire_node})
        return wire_node


class UpdateWireHandler(CommandHandler):
    def execute(self, cmd: wire_domain.UpdateWire) -> wire_domain.Wire:
        logger.info("UpdateWire.execute()")

        # Update node
        wire_node = self._repo.get_by_id(cmd.uuid)
        wire_node.set_node_fields(**cmd.model_dump(exclude_none=True, exclude={"uuid"}))
        return wire_node


class WireCreatedHandler(EventHandler):
    def handle(self, event: wire_domain.WireCreated):
        self._repo.add(event.entity)


class WireUpdatedHandler(EventHandler):
    def handle(self, event: wire_domain.WireUpdated):
        # Save
        self._repo.update(event.new_value)

        # Update subscribers
        subs: set[wire_domain.WireSubscriber] = self._repo.get_node_children(event.new_value)
        for sub in subs:
            sub.on_wire_updated(event.old_value, event.new_value)


WIRE_COMMAND_HANDLERS = {
    wire_domain.CreateWire: CreateWireHandler,
    wire_domain.UpdateWire: UpdateWireHandler,
}

WIRE_EVENT_HANDLERS = {
    wire_domain.WireCreated: WireCreatedHandler,
    wire_domain.WireUpdated: WireUpdatedHandler,
}
