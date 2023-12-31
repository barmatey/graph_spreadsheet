from loguru import logger

from src.pubsub.handlers import CommandHandler
from . import domain as group_sheet_domain


class GetSheetByIdHandler(CommandHandler):
    def execute(self, cmd: group_sheet_domain.GetSheetById) -> group_sheet_domain.GroupSheet:
        raise NotImplemented


class CreateGroupSheetHandler(CommandHandler):
    def execute(self, cmd: group_sheet_domain.CreateGroupSheet) -> group_sheet_domain.GroupSheet:
        # Get wires
        source = self._repo.get_by_id(cmd.source_id)

        # Create
        plan_items = group_sheet_domain.PlanItems(ccols=cmd.ccols)
        group_sheet = group_sheet_domain.GroupSheet(uuid=cmd.uuid, plan_items=plan_items)
        group_sheet.follow_source(source)

        return group_sheet


GROUP_COMMAND_HANDLERS = {
    group_sheet_domain.CreateGroupSheet: CreateGroupSheetHandler,
    group_sheet_domain.GetSheetById: GetSheetByIdHandler,
}
