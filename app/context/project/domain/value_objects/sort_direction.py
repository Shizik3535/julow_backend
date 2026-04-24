from __future__ import annotations

from enum import Enum


class SortDirection(Enum):
    """
    Направление сортировки.

    Значения:
        ASC: По возрастанию
        DESC: По убыванию
    """

    ASC = "asc"
    DESC = "desc"
