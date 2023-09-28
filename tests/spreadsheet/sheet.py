import pytest

from src.spreadsheet.cell.domain import SheetCell
from src.spreadsheet.sheet.domain import Sheet, RowsAppended, RowsDeleted, RowsReindexed


@pytest.fixture(scope="function")
def sheet():
    sheet = Sheet()
    rows = [
        [SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)],
        [SheetCell(index=(1, 0), value=11), SheetCell(index=(1, 1), value=12)],
        [SheetCell(index=(2, 0), value=11), SheetCell(index=(2, 1), value=12)],
        [SheetCell(index=(3, 0), value=11), SheetCell(index=(3, 1), value=12)],
        [SheetCell(index=(4, 0), value=11), SheetCell(index=(4, 1), value=12)],
    ]
    sheet.append_rows(rows)
    sheet.parse_events()
    return sheet


def test_create_sheet():
    sheet = Sheet()
    assert sheet.size == (0, 0)


def test_append_row_change_size():
    sheet = Sheet()
    row = [SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)]
    sheet.append_rows(row)
    assert sheet.size == (1, 2)


def test_delete_rows(sheet):
    sheet.delete_rows([1, 2])

    expected = [
        [SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)],
        [SheetCell(index=(1, 0), value=11), SheetCell(index=(1, 1), value=12)],
        [SheetCell(index=(2, 0), value=11), SheetCell(index=(2, 1), value=12)],
    ]
    assert sheet.size == (3, 2)
    for i in range(0, sheet.size[0]):
        for j in range(0, sheet.size[1]):
            assert sheet.table[i][j] == expected[i][j]


def test_sheet_events_have_properly_order(sheet: Sheet):
    sheet.delete_rows([2, 3])
    sheet.append_rows([SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)])
    events = sheet.parse_events()
    assert len(events) == 3
    assert type(events[0]) == RowsDeleted
    assert type(events[1]) == RowsAppended
    assert type(events[2]) == RowsReindexed

