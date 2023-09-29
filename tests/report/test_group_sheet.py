import pytest

from src.node.repository import GraphRepoFake
from src.report.sheet.group_sheet import PlanItems
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.report.sheet.group_sheet import domain as group_domain
from tests.report.before import execute, load_data, source_uuid, wire2_uuid, group_sheet_uuid


@pytest.fixture(scope="module")
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
    expected_parents = {repo.get_by_id(source_uuid)}
    real_parents = repo.get_node_parents(group_sheet)
    assert real_parents == expected_parents


def test_created_group_sheet_has_properly_table(repo):
    expected = [
        [1.0, "Hello"],
        [2.0, "World"],
        [3.0, "Anna!"]
    ]
    real: group_domain.GroupSheetNode = repo.get_by_id(group_sheet_uuid).get_as_simple_table()
    assert str(real) == str(expected)


def test_group_sheet_cells_react_on_wire_change(repo):
    cmd = wire_domain.UpdateWire(uuid=wire2_uuid, sub1="Updated")
    execute(cmd)
    expected = [
        [1.0, "Hello"],
        [3.0, "Anna!"],
        [2.0, "Updated"]
    ]
    real = repo.get_by_id(group_sheet_uuid).get_as_simple_table()
    assert str(real) == str(expected)


def test_plan_items_uniques_react_on_wire_change(repo):
    expected = {
        "[1.0, 'Hello']": 1,
        "[3.0, 'Anna!']": 1,
        "[2.0, 'Updated']": 1,
    }
    real = repo.get_by_id(group_sheet_uuid).plan_items.uniques
    assert real == expected


def test_group_sheet_drop_duplicates():
    wire1 = wire_domain.WireNode(sender=1, receiver=2, amount=0, sub1="Hello")
    wire2 = wire_domain.WireNode(sender=1, receiver=2, amount=0, sub1="Hello")
    source = source_domain.Source(title="Source")
    source.follow_wires({wire1, wire2})
    plan_items = PlanItems(ccols=["sender", "sub1"])
    sheet = group_domain.GroupSheetNode(plan_items=plan_items)
    sheet.follow_source(source)

    actual = sheet.get_as_simple_table()
    expected = [[1.0, "Hello"]]
    assert str(actual) == str(expected)
