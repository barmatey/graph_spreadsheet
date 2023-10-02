import pandas as pd

from src.report.formula.period import domain as period_domain
from src.report.formula.mapper import domain as mapper_domain
from src.report.sheet.group_sheet import domain as group_domain
from src.report.source import domain as source_domain
from src.spreadsheet.sindex.domain import Sindex
from . import domain as pf_domain


class CreateProfitSheetUsecase:
    def __init__(self, cmd: pf_domain.CreateProfitSheet, group: group_domain.GroupSheet, source: source_domain.Source):
        self._cmd = cmd
        self._group_sheet: group_domain.GroupSheet = group
        self._source: source_domain.Source = source
        self._periods: list[period_domain.Period] | None = None
        self._mappers: list[mapper_domain.Mapper] | None = None
        self._result: pf_domain.ProfitSheet | None = None

    def _create_periods(self):
        start_date = self._cmd.start_date
        end_date = self._cmd.end_date
        period = self._cmd.period
        freq = self._cmd.freq
        date_range = [x.to_pydatetime() for x in pd.date_range(start_date, end_date, freq=f"{period}{freq}")]
        periods = []
        for start, end in zip(date_range[:-1], date_range[1:]):
            period = period_domain.Period(from_date=start, to_date=end)
            periods.append(period)
        self._periods = periods

    def _create_mappers(self):
        group_sheet = self._group_sheet
        mappers = []
        for i in range(0, group_sheet.size[0]):
            mapper = mapper_domain.Mapper(ccols=group_sheet.plan_items.ccols)
            pubs = set()
            for j in range(group_sheet.size[1]):
                cell = group_sheet.table[i][j]
                pubs.add(cell)
            mapper.follow_cell_publishers(pubs)
            mappers.append(mapper)
        self._mappers = mappers

    def _create_blank_profit_sheet(self):
        sheet_meta = pf_domain.ProfitSheetMeta(ccols=self._group_sheet.plan_items.ccols, periods=self._periods,
                                               source_id=self._cmd.source_id)
        profit_sheet = pf_domain.ProfitSheet(uuid=self._cmd.uuid, meta=sheet_meta)
        profit_sheet.follow_sheet(self._group_sheet)
        self._result = profit_sheet

    def _create_first_row(self):
        left_indexes_len = self._group_sheet.size[1]

        cells = []
        row_sindex = Sindex(position=0)

        # Create index cells (left corner, blank values)
        for j in range(0, left_indexes_len):
            col_sindex = Sindex(position=j)
            cell = pf_domain.ProfitPeriodCell(row_index=row_sindex, col_index=col_sindex, value=None)
            cells.append(cell)

        # Create table cells
        for j, period in enumerate(self._periods, start=left_indexes_len):
            profit_cell = pf_domain.ProfitPeriodCell(row_index=Sindex(position=0), col_index=Sindex(position=j),
                                                     value=0)
            profit_cell.follow_periods({period})
            cells.append(profit_cell)
        self._result.append_rows(row_sindex, cells)

    def _create_table_rows(self):
        left_indexes_len = self._group_sheet.size[1]

        table: list[list[pf_domain.ProfitCell]] = []
        row_sindexes: list[Sindex] = []

        for i, mapper in enumerate(self._mappers, start=1):
            row_sindex = Sindex(position=i)
            row_sindexes.append(row_sindex)

            cells = []
            # Index cells (left part)
            for j in range(0, left_indexes_len):
                col_sindex = Sindex(position=j)
                cell = pf_domain.ProfitMapperCell(row_index=row_sindex, col_index=col_sindex, value=None)
                cell.follow_mappers({mapper})
                cells.append(cell)

            # Table cells
            for j, period in enumerate(self._periods, start=left_indexes_len):
                col_sindex = Sindex(position=j)
                profit_cell = pf_domain.ProfitCell(row_index=row_sindex, col_index=col_sindex, value=0)
                profit_cell.follow_periods({period})
                profit_cell.follow_mappers({mapper})
                profit_cell.follow_source(self._source)
                cells.append(profit_cell)
            table.append(cells)
        self._result.append_rows(row_sindexes, table)

    def execute(self) -> pf_domain.ProfitSheet:
        self._create_mappers()
        self._create_periods()
        self._create_blank_profit_sheet()
        self._create_first_row()
        self._create_table_rows()
        return self._result


class AppendRowsUsecase:
    def __init__(self, sheet: pf_domain.ProfitSheet, rows: list[Sindex], table: list[list[pf_domain.SheetCell]],
                 source: source_domain.Source):
        self._sheet = sheet
        self._source = source
        self._pub_rows = rows
        self._pub_table = table
        self._mappers: list[mapper_domain.Mapper] = []

    def _create_mappers(self):
        for row in self._pub_table:
            mapper = mapper_domain.Mapper(ccols=self._sheet.meta.ccols)
            mapper.follow_cell_publishers(row)
            self._mappers.append(mapper)

    def _create_rows(self):
        table: list[list[pf_domain.SheetCell]] = []
        sindexes: list[Sindex] = []

        i = self._sheet.size[0]
        for pub_sindex, pub_cells, mapper in zip(self._pub_rows, self._pub_table, self._mappers):
            sindex = Sindex(position=i)
            sindexes.append(sindex)

            table_row = []

            # Create index part (left part)
            for j, pub_cell in enumerate(pub_cells):
                col_sindex = Sindex(position=j)
                left_cell = pf_domain.SheetCell(row_index=sindex, col_index=col_sindex, value=pub_cell.value)
                left_cell.follow_cell_publishers({pub_cell})
                table_row.append(left_cell)

            # Create table part
            for j, period in enumerate(self._sheet.meta.periods, start=len(pub_cells)):
                col_sindex = Sindex(position=j)
                cell = pf_domain.ProfitCell(row_index=sindex, col_index=col_sindex, value=0)
                cell.follow_mappers({mapper})
                cell.follow_periods({period})
                cell.follow_source(self._source)
                table_row.append(cell)

            table.append(table_row)
            i += 1
        self._sheet.append_rows(sindexes, table)

    def execute(self) -> pf_domain.ProfitSheet:
        self._create_mappers()
        self._create_rows()
        return self._sheet
