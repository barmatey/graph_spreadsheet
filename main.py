from loguru import logger
from pydantic import BaseModel

from src.messagebus.msgbus import Msgbus
from src.node.repository import GraphRepoFake
from src.source import domain as source_domain
from src.wire import domain as wire_domain

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
    cmd_wire = wire_domain.CreateWireNode(sender=1, receiver=2, amount=333, source_id=source.uuid)
    wire = execute(cmd_wire)

    # Wire update
    cmd_wire_update = wire_domain.UpdateWire(uuid=wire.uuid, sender=330)
    execute(cmd_wire_update)

    logger.success(source)
    logger.success(repo.get_by_id(wire.uuid).sender)


if __name__ == '__main__':
    print_hi()
