from uuid import uuid4
from datetime import datetime

import pytest

from src.node.repository import GraphRepoFake
from src.report.finrep_sheet import domain as fr_domain
from src.report.source import domain as source_domain
from src.report.wire import domain as wire_domain
from src.report.group_sheet import domain as group_domain

from .before import execute

sheet_id = uuid4()
source_id = uuid4()
group_id = uuid4()

wire1_id = uuid4()
wire2_id = uuid4()
wire3_id = uuid4()
wire4_id = uuid4()


def load_data():
    cmd_source = source_domain.CreateSourceNode(uuid=source_id, title="Source")
    cmd_wire1 = wire_domain.CreateWireNode(date=datetime(2021, 5, 5), uuid=wire1_id, source_id=source_id,
                                           sender=1, receiver=2, amount=10, sub1="Profit", )
    cmd_wire2 = wire_domain.CreateWireNode(date=datetime(2022, 5, 5), uuid=wire2_id, source_id=source_id,
                                           sender=1, receiver=2, amount=30, sub1="Profit", )
    cmd_wire3 = wire_domain.CreateWireNode(date=datetime(2021, 5, 5), uuid=wire3_id, source_id=source_id,
                                           sender=2, receiver=2, amount=33, sub1="Expenses", )
    cmd_wire4 = wire_domain.CreateWireNode(date=datetime(2022, 5, 5), uuid=wire4_id, source_id=source_id,
                                           sender=1, receiver=2, amount=44, sub1="Expenses", )
    cmd_group = group_domain.CreateGroupSheetNode(uuid=group_id, source_id=source_id, ccols=["sender", "sub1"])
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
    cmd = fr_domain.CreateProfitSheetNode(
        uuid=sheet_id,
        source_id=source_id,
        group_id=group_id,
        start_date=datetime(2021, 1, 1),
        end_date=datetime(2023, 1, 1),
        period=1,
        freq='Y'
    )
    sheet: fr_domain.FinrepSheet = execute(cmd)

    # expected = [
    #     ['', '', datetime(2022, 1, 1), datetime(2023, 1, 1)],
    #     [1, 'Profit', 10, 30],
    #     [2, 'Expenses', 33, 44],
    # ]
    expected = [
        [datetime(2022, 1, 1), datetime(2023, 1, 1)],
        [10, 30],
        [33, 44],
    ]
    assert str(sheet.get_as_simple_table()) == str(expected)
