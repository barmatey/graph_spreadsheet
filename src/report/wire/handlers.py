from loguru import logger

from src.node.handlers import CommandHandler
from . import domain as wire_domain
from src.report.source import domain as source_domain


class CreateWireNodeHandler(CommandHandler):
    def execute(self, cmd: wire_domain.CreateWireNode) -> wire_domain.WireNode:
        logger.info("CreateWireNode.execute()")

        # Create wire node
        wire_node = wire_domain.WireNode(**cmd.model_dump(exclude={"source_id"}))
        self._repo.add(wire_node)

        # Append wire to source
        source_node: source_domain.SourceNode = self._repo.get_by_id(cmd.source_id)
        source_node.append_wires([wire_node])

        self.extend_events(wire_node.parse_events())
        self.extend_events(source_node.parse_events())

        return wire_node


class UpdateWireHandler(CommandHandler):
    def execute(self, cmd: wire_domain.UpdateWire) -> wire_domain.WireNode:
        logger.info("UpdateWire.execute()")

        # Update node
        wire_node = self._repo.get_by_id(cmd.uuid).model_copy(deep=True)
        wire_node.set_node_fields(cmd.model_dump(exclude_none=True, exclude={"uuid"}))
        self.extend_events(wire_node.parse_events())
        return wire_node



WIRE_COMMAND_HANDLERS = {
    wire_domain.CreateWireNode: CreateWireNodeHandler,
    wire_domain.UpdateWire: UpdateWireHandler,
}
