from src.node.domain import Command
from src.node.handlers import CommandHandler
from src.source.handlers import SOURCE_COMMAND_HANDLERS
from src.wire.handlers import WIRE_COMMAND_HANDLERS
from src.formula.utable.handlers import UTABLE_COMMAND_HANDLERS
from src.formula.mapper.handlers import MAPPER_COMMAND_HANDLERS

COMMAND_HANDLERS = (
    WIRE_COMMAND_HANDLERS
    | SOURCE_COMMAND_HANDLERS
    | UTABLE_COMMAND_HANDLERS
    | MAPPER_COMMAND_HANDLERS
)


def get_command_handler(cmd: Command) -> CommandHandler:
    handler = COMMAND_HANDLERS[type(cmd)]()
    return handler
