from src.messagebus.msgbus import Msgbus
from src.node.repository import GraphRepoFake
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.spreadsheet.formula.utable import domain as utable_domain
from src.report.formula.mapper import domain as mapper_domain
from src.report.formula.profit_cell import domain as pf_domain
from src.report.formula.period import domain as period_domain
from src.spreadsheet.sheet import domain as group_domain
from datetime import datetime

bus = Msgbus()
repo = GraphRepoFake()


def execute(cmd):
    bus.push_command(cmd)
    bus.run()
    return bus.results[cmd.uuid]


def foo():
    # Source
    cmd_source = source_domain.CreateSourceNode(title="Hello")
    source = execute(cmd_source)

    # Wire
    cmd_wire1 = wire_domain.CreateWireNode(sender=1, receiver=2, amount=1, sub1="Hello", source_id=source.uuid)
    cmd_wire2 = wire_domain.CreateWireNode(sender=2, receiver=2, amount=1, sub1="World", source_id=source.uuid)
    cmd_wire3 = wire_domain.CreateWireNode(sender=3, receiver=2, amount=1, sub1="Anna!", source_id=source.uuid)
    execute(cmd_wire1)
    execute(cmd_wire2)
    execute(cmd_wire3)

    cmd_group = group_domain.CreateGroupSheetNode(title="Hello", source_id=source.uuid, ccols=["sender", "sub1"])
    group_sheet = execute(cmd_group)

    for row in group_sheet.table:
        print(row)


def print_hi():
    # Source
    cmd_source = source_domain.CreateSourceNode(title="Hello")
    source = execute(cmd_source)

    # Wire
    cmd_wire1 = wire_domain.CreateWireNode(sender=1, receiver=2, amount=1, source_id=source.uuid)
    cmd_wire2 = wire_domain.CreateWireNode(sender=2, receiver=2, amount=1, source_id=source.uuid)
    cmd_wire3 = wire_domain.CreateWireNode(sender=3, receiver=2, amount=1, source_id=source.uuid)

    wire1 = execute(cmd_wire1)
    wire2 = execute(cmd_wire2)
    wire3 = execute(cmd_wire3)

    # Utable
    cmd_utable = utable_domain.CreateUtableNode(source_id=source.uuid, ccols=["sender", "sub1"])
    utable = execute(cmd_utable)

    # Mapper
    cmd_mapper0 = mapper_domain.CreateMapperNode(utable_id=utable.uuid, row_index=0)
    cmd_mapper1 = mapper_domain.CreateMapperNode(utable_id=utable.uuid, row_index=1)
    mapper0 = execute(cmd_mapper0)
    # mapper1 = execute(cmd_mapper1)

    # Period
    cmd_period = period_domain.CreatePeriodNode(from_date=datetime(2020, 1, 1), to_date=datetime(2222, 1, 1))
    period = execute(cmd_period)

    # ProfitCell
    cmd_pf = pf_domain.CreateProfitCellNode(mapper_node_id=mapper0.uuid, source_node_id=source.uuid, period_node_id=period.uuid)
    profit_cell = execute(cmd_pf)

    # Wire update
    cmd_wire_update = wire_domain.UpdateWire(uuid=wire3.uuid, sender=1)
    execute(cmd_wire_update)


if __name__ == '__main__':
    foo()
