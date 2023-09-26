from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from src.node.domain import Event, Command
from src.spreadsheet.sheet import domain as sheet_domain


class FinrepSheet(sheet_domain.SheetNode):
    uuid: UUID = Field(default_factory=uuid4)
    events: list[Event] = Field(default_factory=list)


class CreateProfitSheetNode(Command):
    source_id: UUID
    group_id: UUID
    start_date: datetime
    end_date: datetime
    period: int = 3
    freq: Literal['H', 'D', 'M', 'Y'] = 'M'
    uuid: UUID = Field(default_factory=uuid4)
