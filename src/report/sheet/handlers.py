from loguru import logger

from src.node.handlers import CommandHandler
from src.report.wire import domain as wire_domain
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.utable import domain as utable_domain
from src.sheet.cell import domain as cell_domain
from . import domain as group_domain


class CreateGroupSheetNodeHandler(CommandHandler):
    def execute(self, cmd: group_domain.CreateGroupSheetNode) -> group_domain.SheetNode:
        logger.error("CreateGroup.execute()")

        # Get wires
        source = self._repo.get_by_id(cmd.source_id)
        wires = set(filter(lambda x: isinstance(x, wire_domain.WireNode), self._repo.get_node_parents(source)))

        # Create
        group = group_domain.SheetNode()
        self._repo.add(group)

        utable = utable_domain.UtableNode(ccols=cmd.ccols)
        self._repo.add(utable)
        utable.follow(wires)
        self.extend_events(utable.parse_events())

        for i in range(0, len(utable.utable)):
            for j in range(0, len(utable.utable[0])):
                cell = cell_domain.CellNode(index=(i, j), value=utable.utable[i][j])
                self._repo.add(cell)

        for i in range(0, len(utable.utable)):
            mapper = mapper_domain.MapperNode(index=i)
            self._repo.add(mapper)
            mapper.follow({utable})
            for j in range(0, len(utable.utable[0])):
                cell = cell_domain.CellNode(index=(i, j), value=utable.utable[i][j])
                self._repo.add(cell)
                cell.follow({mapper})
            self.extend_events(mapper.parse_events())

        return group


GROUP_COMMAND_HANDLERS = {
    group_domain.CreateGroupSheetNode: CreateGroupSheetNodeHandler
}
