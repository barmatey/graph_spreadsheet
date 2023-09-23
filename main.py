from loguru import logger
from pydantic import BaseModel

from src.messagebus.msgbus import Msgbus
from src.node.repository import GraphRepoFake
from src.source import domain as source_domain
from src.wire import domain as wire_domain
from src.formula.utable import domain as utable_domain

bus = Msgbus()
repo = GraphRepoFake()


def execute(cmd):
    bus.push_command(cmd)
    bus.run()
    return bus.results[cmd.uuid]


def print_hi():
    # Source
    cmd_source = source_domain.CreateSourceNode(title="Hello")
    source = execute(cmd_source)

    # Wire
    cmd_wire1 = wire_domain.CreateWireNode(sender=1, receiver=2, amount=333, source_id=source.uuid)
    cmd_wire2 = wire_domain.CreateWireNode(sender=1, receiver=2, amount=333, source_id=source.uuid)
    cmd_wire3 = wire_domain.CreateWireNode(sender=1, receiver=2, amount=333, source_id=source.uuid)

    wire1 = execute(cmd_wire1)
    wire2 = execute(cmd_wire2)
    wire3 = execute(cmd_wire3)

    # Utable
    cmd_utable = utable_domain.CreateUtableNode(source_id=source.uuid, ccols=["sender", "sub1"])
    utable = execute(cmd_utable)

    # Wire update
    cmd_wire_update = wire_domain.UpdateWire(uuid=wire1.uuid, sender=33)
    execute(cmd_wire_update)

    logger.success(utable.utable)


if __name__ == '__main__':
    print_hi()
