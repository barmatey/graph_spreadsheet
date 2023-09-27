from uuid import uuid4

import pytest

from src.messagebus.msgbus import Msgbus
from src.node.domain import Node
from src.node.repository import GraphRepo, GraphRepoFake
from src.report.source.domain import CreateSourceNode, SourceNode
from src.report.wire.domain import CreateWireNode, WireNode

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
    cmd = CreateSourceNode(uuid=source_uuid, title="Hello")
    source = execute(cmd)
    assert source.title == "Hello"


def test_get_source_node_from_repo(repo):
    source = repo.get_by_id(source_uuid)
    assert source.title == "Hello"


def test_create_wire_node(repo: GraphRepo):
    cmd = CreateWireNode(uuid=wire1_uuid, source_id=source_uuid, sender=1, receiver=2, amount=111, sub1="Great")
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
    source: SourceNode = repo.get_by_id(source_uuid)
    assert len(source.wires) == 1
    assert source.wires[0].uuid == wire.uuid

    source_pubs: set[Node] = repo.get_node_parents(source)
    wire_subs: set[Node] = repo.get_node_children(wire)

    assert wire in source_pubs
    assert source in wire_subs