from src.spreadsheet.cell.domain import SheetCell
from src.spreadsheet.sheet.domain import Sheet


def test_create_sheet():
    sheet = Sheet()
    assert sheet.size == (0, 0)


def test_append_row_change_size():
    sheet = Sheet()
    row = [SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)]
    sheet.append_rows(row)
    assert sheet.size == (1, 2)


def test_delete_rows():
    sheet = Sheet()
    rows = [
        [SheetCell(index=(0, 0), value=11), SheetCell(index=(0, 1), value=12)],
        [SheetCell(index=(1, 0), value=11), SheetCell(index=(1, 1), value=12)],
        [SheetCell(index=(2, 0), value=11), SheetCell(index=(2, 1), value=12)],
        [SheetCell(index=(3, 0), value=11), SheetCell(index=(3, 1), value=12)],
        [SheetCell(index=(4, 0), value=11), SheetCell(index=(4, 1), value=12)],
    ]
    sheet.append_rows(rows)

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
