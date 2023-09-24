from loguru import logger

from src.node.handlers import CommandHandler
from . import domain as source_domain


class CreateSourceNodeHandler(CommandHandler):
    def execute(self, cmd: source_domain.CreateSourceNode) -> source_domain.SourceNode:
        logger.info("CreateSourceNode.execute()")
        source_node = source_domain.SourceNode(title=cmd.title)
        self._repo.add(source_node)
        return source_node


SOURCE_COMMAND_HANDLERS = {
    source_domain.CreateSourceNode: CreateSourceNodeHandler,
}

