from __future__ import annotations

from enum import Enum


class FilterOperator(Enum):
    """
    Оператор фильтрации.

    Значения:
        EQ: Равно
        NEQ: Не равно
        IN: Входит в
        NOT_IN: Не входит в
        CONTAINS: Содержит
        GT: Больше
        LT: Меньше
        GTE: Больше или равно
        LTE: Меньше или равно
        IS_EMPTY: Пустое
        IS_NOT_EMPTY: Не пустое
    """

    EQ = "eq"
    NEQ = "neq"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
