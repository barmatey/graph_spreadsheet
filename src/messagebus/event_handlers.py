from src.node.domain import Event
from src.node.handlers import EventHandler, COMMON_EVENT_HANDLERS
from src.formula.profit_cell.handlers import PROFIT_CELL_EVENT_HANDLERS

EVENT_HANDLERS = (
    COMMON_EVENT_HANDLERS
    | PROFIT_CELL_EVENT_HANDLERS
)


def get_event_handler(event: Event) -> EventHandler:
    handler = EVENT_HANDLERS[type(event)]()
    return handler
