from loguru import logger

from src.messagebus.msgbus import Msgbus
from src.node.domain import Node
from src.node.repository import GraphRepoFake
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.report.group_sheet import domain as group_domain
from src.report.finrep_sheet import domain as report_domain
from datetime import datetime

bus = Msgbus()
repo = GraphRepoFake()


def print_graph(node: Node):
    level = 0
    string = "\n"

    def print_node(n: Node):
        nonlocal level
        nonlocal string
        string = string + "-" * level + f"{n}\n"
        for sub in repo.get_node_children(n):
            level += 1
            print_node(sub)
            level -= 1

    print_node(node)
    print(string)


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

    cmd_profit = report_domain.CreateProfitSheetNode(
        source_id=source.uuid,
        group_id=group_sheet.uuid,
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2025, 1, 1),
        freq='M',
        period=12,
    )
    profit_node = execute(cmd_profit)

    print_graph(group_sheet)
    print()
    print_graph(profit_node)


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


    # Wire update
    cmd_wire_update = wire_domain.UpdateWire(uuid=wire3.uuid, sender=1)
    execute(cmd_wire_update)


if __name__ == '__main__':
    foo()
