from typing import Union
from datetime import datetime
from abc import ABC, abstractmethod


CellValue = Union[int, float, str, bool, None, datetime]
CellTable = list[list[CellValue]]
