from src.node.domain import Event
from src.node.handlers import EventHandler, COMMON_EVENT_HANDLERS
from src.report.source.handlers import SOURCE_EVENT_HANDLERS
from src.report.formula.profit_cell.handlers import PROFIT_CELL_EVENT_HANDLERS
from src.report.wire.handlers import WIRE_EVENT_HANDLERS
from src.spreadsheet.sheet.handlers import SHEET_EVENT_HANDLERS
from src.spreadsheet.cell.handlers import CELL_EVENT_HANDLERS
from src.report.formula.mapper.handlers import MAPPER_EVENT_HANDlERS

EVENT_HANDLERS = (
        COMMON_EVENT_HANDLERS
        | SOURCE_EVENT_HANDLERS
        | PROFIT_CELL_EVENT_HANDLERS
        | WIRE_EVENT_HANDLERS
        | SHEET_EVENT_HANDLERS
        | MAPPER_EVENT_HANDlERS
        | CELL_EVENT_HANDLERS
)


def get_event_handler(event: Event) -> EventHandler:
    handler = EVENT_HANDLERS[type(event)]()
    return handler
