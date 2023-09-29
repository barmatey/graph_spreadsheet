from src.node.domain import Command
from src.node.handlers import CommandHandler
from src.report.source.handlers import SOURCE_COMMAND_HANDLERS
from src.report.wire.handlers import WIRE_COMMAND_HANDLERS
from src.report.formula.mapper.handlers import MAPPER_COMMAND_HANDLERS
from src.report.formula.period.handlers import PERIOD_COMMAND_HANDLERS
from src.report.sheet.group_sheet.handlers import GROUP_COMMAND_HANDLERS
from src.report.sheet.profit_sheet.handlers import PROFIT_SHEET_COMMAND_HANDLERS, PROFIT_CELL_COMMAND_HANDLERS

COMMAND_HANDLERS = (
        WIRE_COMMAND_HANDLERS
        | SOURCE_COMMAND_HANDLERS
        | MAPPER_COMMAND_HANDLERS
        | PROFIT_CELL_COMMAND_HANDLERS
        | PERIOD_COMMAND_HANDLERS
        | GROUP_COMMAND_HANDLERS
        | PROFIT_SHEET_COMMAND_HANDLERS
)


def get_command_handler(cmd: Command) -> CommandHandler:
    handler = COMMAND_HANDLERS[type(cmd)]()
    return handler
