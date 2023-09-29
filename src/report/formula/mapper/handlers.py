from loguru import logger

from src.node.handlers import CommandHandler, EventHandler
from . import domain as mapper_domain


class CreateMapperNodeHandler(CommandHandler):
    def execute(self, cmd: mapper_domain.CreateMapperNode) -> mapper_domain.MapperNode:
        logger.info("CreateMapperNode.execute()")
        mapper_node = mapper_domain.MapperNode(index=cmd.row_index)
        self._repo.add(mapper_node)

        utable_node = self._repo.get_by_id(cmd.utable_id)
        mapper_node.follow({utable_node})
        self.extend_events(mapper_node.parse_events())
        return mapper_node


class MapperUpdatedHandler(EventHandler):
    def handle(self, event: mapper_domain.MapperUpdated):
        logger.debug("MapperUpdated.handle()")
        self._repo.update(event.new_value)


MAPPER_COMMAND_HANDLERS = {
    mapper_domain.CreateMapperNode: CreateMapperNodeHandler,
}

MAPPER_EVENT_HANDlERS = {
    mapper_domain.MapperUpdated: MapperUpdatedHandler,
}
