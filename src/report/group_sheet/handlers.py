from loguru import logger

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.report.formula.utable import domain as utable_domain
from src.report.formula.mapper import domain as mapper_domain
from src.spreadsheet.cell import domain as cell_domain
from . import domain as sheet_domain


class GetSheetByIdHandler(CommandHandler):
    def execute(self, cmd: sheet_domain.GetSheetById) -> sheet_domain.SheetNode:
        raise NotImplemented


class CreateGroupSheetNodeHandler(CommandHandler):
    def execute(self, cmd: sheet_domain.CreateGroupSheetNode) -> sheet_domain.SheetNode:
        logger.error("CreateGroup.execute()")

        # Get wires
        source = self._repo.get_by_id(cmd.source_id)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))

        # Create
        utable = utable_domain.UtableNode(ccols=cmd.ccols)
        self._repo.add(utable)
        utable.follow(wires)
        self.extend_events(utable.parse_events())

        group = sheet_domain.SheetNode()
        self._repo.add(group)

        for i in range(0, len(utable.value)):
            row = []
            mapper = mapper_domain.MapperNode(ccols=cmd.ccols)
            self._repo.add(mapper)
            for j in range(0, len(utable.value[0])):
                cell = cell_domain.CellNode(index=(i, j), value=utable.value[i][j])
                self._repo.add(cell)
                cell.follow({utable})
                row.append(cell.value)
                self.extend_events(cell.parse_events())
                mapper.follow({cell})
            logger.success(mapper.filter_by)
            self.extend_events(mapper.parse_events())
            group.table.append(row)

        return group


GROUP_COMMAND_HANDLERS = {
    sheet_domain.CreateGroupSheetNode: CreateGroupSheetNodeHandler,
    sheet_domain.GetSheetById: GetSheetByIdHandler,
}
