from uuid import uuid4
from datetime import datetime

import pytest

from src.pubsub.repository import GraphRepoFake
from src.report.sheet.profit_sheet import domain as fr_domain
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.report.sheet.group_sheet import domain as group_domain

from .before import execute

sheet_id = uuid4()
source_id = uuid4()
group_id = uuid4()

wire1_id = uuid4()
wire2_id = uuid4()
wire3_id = uuid4()
wire4_id = uuid4()


def load_data():
    cmd_source = source_domain.CreateSource(uuid=source_id, title="Source")
    cmd_wire1 = wire_domain.CreateWire(date=datetime(2021, 5, 5), uuid=wire1_id, source_id=source_id,
                                       sender=1, receiver=2, amount=10, sub1="Profit", )
    cmd_wire2 = wire_domain.CreateWire(date=datetime(2022, 5, 5), uuid=wire2_id, source_id=source_id,
                                       sender=1, receiver=2, amount=30, sub1="Profit", )
    cmd_wire3 = wire_domain.CreateWire(date=datetime(2021, 5, 5), uuid=wire3_id, source_id=source_id,
                                       sender=2, receiver=2, amount=33, sub1="Expenses", )
    cmd_wire4 = wire_domain.CreateWire(date=datetime(2022, 5, 5), uuid=wire4_id, source_id=source_id,
                                       sender=2, receiver=2, amount=44, sub1="Expenses", )
    cmd_group = group_domain.CreateGroupSheet(uuid=group_id, source_id=source_id, ccols=["sender", "sub1"])
    execute(cmd_source)
    execute(cmd_wire1)
    execute(cmd_wire2)
    execute(cmd_wire3)
    execute(cmd_wire4)
    execute(cmd_group)


@pytest.fixture(scope="module")
def repo():
    repo = GraphRepoFake()
    load_data()
    return repo


def test_create_profit_sheet(repo):
    cmd = fr_domain.CreateProfitSheet(
        uuid=sheet_id,
        source_id=source_id,
        group_id=group_id,
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2022, 12, 31),
        period=1,
        freq='Y'
    )
    sheet: fr_domain.ProfitSheet = execute(cmd)

    actual = sheet.get_as_simple_table()
    expected = [
        [None, None, datetime(2021, 12, 31), datetime(2022, 12, 31)],
        [1.0, 'Profit', 10.0, 30.0],
        [2.0, 'Expenses', 33.0, 44.0],
    ]
    assert str(actual) == str(expected)


def test_update_wire_amount_changes_profit_cell_value(repo):
    cmd = wire_domain.UpdateWire(uuid=wire1_id, amount=777)
    execute(cmd)

    sheet = repo.get_by_id(sheet_id)
    actual = sheet.get_as_simple_table()
    expected = [
        [None, None, datetime(2021, 12, 31), datetime(2022, 12, 31)],
        [1.0, 'Profit', 777.0, 30.0],
        [2.0, 'Expenses', 33.0, 44.0],
    ]
    assert str(actual) == str(expected)

#
# def test_append_new_unique_wire_expand_profit_sheet(repo):
#     cmd = wire_domain.CreateWire(source_id=source_id, sender=3, receiver=2, amount=100, sub1="New",
#                                  date=datetime(2021, 5, 5))
#     execute(cmd)
#
#     sheet = repo.get_by_id(sheet_id)
#     actual = sheet.get_as_simple_table()
#     expected = [
#         [None, None, datetime(2021, 12, 31), datetime(2022, 12, 31)],
#         [1.0, 'Profit', 777.0, 30.0],
#         [2.0, 'Expenses', 33.0, 44.0],
#         [3.0, "New", 100.0, 0]
#     ]
#     assert str(actual) == str(expected)
#
#
# def test_profit_sheet_squeeze_after_group_sheet(repo):
#     cmd = wire_domain.UpdateWire(uuid=wire1_id, sender=2, sub1="Expenses")
#     execute(cmd)
#
#     sheet = repo.get_by_id(sheet_id)
#     actual = sheet.get_as_simple_table()
#     expected = [
#         [None, None, datetime(2021, 12, 31), datetime(2022, 12, 31)],
#         [2.0, 'Expenses', 33.0, 44.0],
#         [3.0, "New", 100.0, 0]
#     ]
#     assert str(actual) == str(expected)
