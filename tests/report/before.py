from uuid import uuid4

from src.messagebus.msgbus import Msgbus
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain


def execute(cmd):
    bus = Msgbus()
    bus.push_command(cmd)
    bus.run()
    result = bus.results[cmd.uuid]
    return result


def load_data():
    # Source
    cmd_source = source_domain.CreateSource(uuid=source_uuid, title="Hello")
    source = execute(cmd_source)

    # Wire
    cmd_wire1 = wire_domain.CreateWireNode(uuid=wire1_uuid, sender=1, receiver=11, amount=1, sub1="Hello",
                                           source_id=source.uuid)
    cmd_wire2 = wire_domain.CreateWireNode(uuid=wire2_uuid, sender=2, receiver=22, amount=3, sub1="World",
                                           source_id=source.uuid)
    cmd_wire3 = wire_domain.CreateWireNode(uuid=wire3_uuid, sender=3, receiver=33, amount=12, sub1="Anna!",
                                           source_id=source.uuid)
    execute(cmd_wire1)
    execute(cmd_wire2)
    execute(cmd_wire3)


source_uuid = uuid4()
wire1_uuid = uuid4()
wire2_uuid = uuid4()
wire3_uuid = uuid4()
group_sheet_uuid = uuid4()
