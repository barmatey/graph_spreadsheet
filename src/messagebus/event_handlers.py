from src.pubsub.domain import Event
from src.pubsub.handlers import EventHandler, COMMON_EVENT_HANDLERS
from src.report.source.handlers import SOURCE_EVENT_HANDLERS
from src.report.sheet.profit_sheet.handlers import PROFIT_CELL_EVENT_HANDLERS
from src.report.wire.handlers import WIRE_EVENT_HANDLERS
from src.spreadsheet.sheet.handlers import SHEET_EVENT_HANDLERS
from src.spreadsheet.cell.handlers import CELL_EVENT_HANDLERS
from src.report.formula.mapper.handlers import MAPPER_EVENT_HANDlERS
from src.report.sheet.profit_sheet.handlers import PROFIT_SHEET_EVENT_HANDLERS

EVENT_HANDLERS = (
        COMMON_EVENT_HANDLERS
        | SOURCE_EVENT_HANDLERS
        | PROFIT_CELL_EVENT_HANDLERS
        | WIRE_EVENT_HANDLERS
        | SHEET_EVENT_HANDLERS
        | MAPPER_EVENT_HANDlERS
        | CELL_EVENT_HANDLERS
        | PROFIT_SHEET_EVENT_HANDLERS
)


def get_event_handler(event: Event) -> EventHandler:
    handler = EVENT_HANDLERS[type(event)]()
    return handler
