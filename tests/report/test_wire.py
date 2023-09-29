from uuid import uuid4

import pytest

from src.messagebus.msgbus import Msgbus
from src.node.domain import Node
from src.node.repository import GraphRepo, GraphRepoFake
from src.report.source.domain import CreateSource, Source
from src.report.wire.domain import CreateWire, WireNode

source_uuid = uuid4()
wire1_uuid = uuid4()
wire2_uuid = uuid4()
wire3_uuid = uuid4()


@pytest.fixture()
def repo():
    repo = GraphRepoFake()
    return repo


def execute(cmd):
    bus = Msgbus()
    bus.push_command(cmd)
    bus.run()
    result = bus.results[cmd.uuid]
    return result


def test_create_source_node():
    cmd = CreateSource(uuid=source_uuid, title="Hello")
    source = execute(cmd)
    assert source.title == "Hello"


def test_get_source_node_from_repo(repo):
    source = repo.get_by_id(source_uuid)
    assert source.title == "Hello"


def test_create_wire_node(repo: GraphRepo):
    cmd = CreateWire(uuid=wire1_uuid, source_id=source_uuid, sender=1, receiver=2, amount=111, sub1="Great")
    wire = execute(cmd)
    assert wire.sender == 1
    assert wire.receiver == 2
    assert wire.amount == 111
    assert wire.sub1 == "Great"


def test_get_wire_node_from_repo(repo: GraphRepo):
    wire = repo.get_by_id(wire1_uuid)
    assert wire.uuid == wire1_uuid


def test_created_wire_was_linked_with_source(repo: GraphRepo):
    wire: WireNode = repo.get_by_id(wire1_uuid)
    source: Source = repo.get_by_id(source_uuid)

    source_pubs: set[Node] = repo.get_node_parents(source)
    wire_subs: set[Node] = repo.get_node_children(wire)

    assert wire in source_pubs
    assert source in wire_subs


def test_double_update_wire_create_one_event():
    wire = WireNode(sender=1, receiver=1, amount=22)
    wire.set_node_fields(sender=22)
    wire.set_node_fields(receiver=12)
    events = wire.parse_events()
    assert wire.sender == 22
    assert wire.receiver == 12
    assert len(events) == 1

