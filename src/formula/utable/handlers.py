from collections import deque

from loguru import logger

from src.node.handlers import CommandHandler
from src.wire import domain as wire_domain
from . import domain as utable_domain


class CreateUtableNodeHandler(CommandHandler):
    def execute(self, cmd: utable_domain.CreateUtableNode) -> utable_domain.UtableNode:
        logger.info("CreateUtableNode.execute()")

        # Create blank utable
        utable_node = utable_domain.UtableNode(ccols=cmd.ccols)
        self._repo.add(utable_node)

        # Find wires
        source = self._repo.get_by_id(cmd.source_id)
        all_parents = self._repo.get_node_parents(source)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), all_parents))

        # Subscribing
        utable_node.on_subscribed(wires)
        self._repo.append_node_parents(utable_node, wires)
        self.extend_events(utable_node.parse_events())

        for w in wires:
            self._repo.append_node_children(w, {utable_node})

        return utable_node


UTABLE_COMMAND_HANDLERS = {
    utable_domain.CreateUtableNode: CreateUtableNodeHandler,
}

PLAN_ITEMS_EVENT_HANDLERS = {
}
