from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator


@dataclass(frozen=True)
class FilterConfig(ValueObject):
    """Конфигурация фильтра."""

    field: str = ""
    operator: FilterOperator = FilterOperator.EQ
    value: str = ""
    value_to: str | None = None
