from uuid import UUID

from src.core.cell import CellTable
from src.pubsub.repository import GraphRepoFake
from src.spreadsheet.sheet.domain import Sheet


class GetAsSimpleTable:
    def __init__(self,  sheet_uuid: UUID, repo: GraphRepoFake = GraphRepoFake()):
        self._repo = repo
        self._sheet_uuid = sheet_uuid

    def execute(self) -> CellTable:
        result: CellTable = []
        sheet: Sheet = self._repo.get_by_id(self._sheet_uuid)
        for i in range(0, sheet.size[0]):
            for j in range(0, sheet.size[1]):
                pass

