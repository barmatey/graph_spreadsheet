from loguru import logger

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.report.formula.mapper import domain as mapper_domain
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
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))

        # Create
        group = group_sheet_domain.GroupSheetNode(plan_items=group_sheet_domain.PlanItems(ccols=cmd.ccols))
        self._repo.add(group)

        group.follow(wires)
        self.extend_events(group.parse_events())

        for i in range(0, len(group.plan_items.value)):
            row = []
            mapper = mapper_domain.MapperNode(ccols=cmd.ccols)
            self._repo.add(mapper)
            for j in range(0, len(group.plan_items.value[0])):
                cell = cell_domain.CellNode(index=(i, j), value=group.plan_items.value[i][j])
                self._repo.add(cell)
                cell.follow({group})
                row.append(cell.value)
                self.extend_events(cell.parse_events())
                mapper.follow({cell})
            logger.success(mapper.filter_by)
            self.extend_events(mapper.parse_events())
            group.table.append(row)

        return group


GROUP_COMMAND_HANDLERS = {
    group_sheet_domain.CreateGroupSheetNode: CreateGroupSheetNodeHandler,
    group_sheet_domain.GetSheetById: GetSheetByIdHandler,
}
