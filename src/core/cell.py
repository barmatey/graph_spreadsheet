from typing import Union
from datetime import datetime

CellValue = Union[int, float, str, bool, None, datetime]
CellTable = list[list[CellValue]]
