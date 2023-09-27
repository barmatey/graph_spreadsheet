from uuid import uuid4
import pytest

from src.messagebus.msgbus import Msgbus
from src.node.repository import GraphRepoFake
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.report.group_sheet import domain as group_domain

source_uuid = uuid4()
wire1_uuid = uuid4()
wire2_uuid = uuid4()
wire3_uuid = uuid4()
group_sheet_uuid = uuid4()


def execute(cmd):
    bus = Msgbus()
    bus.push_command(cmd)
    bus.run()
    result = bus.results[cmd.uuid]
    return result


def load_data():
    # Source
    cmd_source = source_domain.CreateSourceNode(uuid=source_uuid, title="Hello")
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


@pytest.fixture()
def repo():
    repo = GraphRepoFake()
    load_data()
    return repo


def test_create_group_sheet(repo):
    cmd_group = group_domain.CreateGroupSheetNode(uuid=group_sheet_uuid, source_id=source_uuid,
                                                  ccols=["sender", "sub1"])
    group_sheet: group_domain.GroupSheetNode = execute(cmd_group)
    assert group_sheet.uuid == group_sheet_uuid


def test_created_group_sheet_has_properly_parents(repo):
    group_sheet = repo.get_by_id(group_sheet_uuid)
    expected_parents = {repo.get_by_id(source_uuid), repo.get_by_id(wire1_uuid), repo.get_by_id(wire2_uuid),
                        repo.get_by_id(wire3_uuid)}
    real_parents = repo.get_node_parents(group_sheet)
    assert expected_parents == real_parents
