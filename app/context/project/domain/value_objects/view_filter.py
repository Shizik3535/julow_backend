from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.filter_operator import FilterOperator


@dataclass(frozen=True)
class ViewFilter(ValueObject):
    """
    Value Object для фильтра представления.

    Атрибуты:
        field: Имя поля.
        operator: Оператор сравнения.
        value: Значение для сравнения.
    """

    field: str
    operator: FilterOperator = FilterOperator.EQ
    value: str = ""
