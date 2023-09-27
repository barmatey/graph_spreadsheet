from loguru import logger

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.spreadsheet.cell import domain as cell_domain
from . import domain as group_sheet_domain


class GetSheetByIdHandler(CommandHandler):
    def execute(self, cmd: group_sheet_domain.GetSheetById) -> group_sheet_domain.GroupSheetNode:
        raise NotImplemented


class CreateGroupSheetNodeHandler(CommandHandler):
    def execute(self, cmd: group_sheet_domain.CreateGroupSheetNode) -> group_sheet_domain.GroupSheetNode:
        logger.error("CreateGroup.execute()")

        # Get wires
        source = self._repo.get_by_id(cmd.source_id)

        # Create
        group_sheet = group_sheet_domain.GroupSheetNode(uuid=cmd.uuid,
                                                        plan_items=group_sheet_domain.PlanItems(ccols=cmd.ccols))
        self._repo.add(group_sheet)

        group_sheet.follow_source(source)
        self.extend_events(group_sheet.parse_events())

        for i in range(0, len(group_sheet.plan_items.value)):
            row = []
            for j in range(0, len(group_sheet.plan_items.value[0])):
                cell = cell_domain.CellNode(index=(i, j), value=group_sheet.plan_items.value[i][j])
                cell.follow({group_sheet})
                self.extend_events(cell.parse_events())
                self._repo.add(cell)
                row.append(cell)
            group_sheet.table.append(row)
        group_sheet.set_node_fields({"size": (len(group_sheet.table), len(group_sheet.table[0]))})

        return group_sheet


GROUP_COMMAND_HANDLERS = {
    group_sheet_domain.CreateGroupSheetNode: CreateGroupSheetNodeHandler,
    group_sheet_domain.GetSheetById: GetSheetByIdHandler,
}
