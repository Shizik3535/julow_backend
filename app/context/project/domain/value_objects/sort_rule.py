from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.sort_direction import SortDirection


@dataclass(frozen=True)
class SortRule(ValueObject):
    """
    Value Object для правила сортировки.

    Атрибуты:
        field: Имя поля.
        direction: Направление сортировки.
    """

    field: str
    direction: SortDirection = SortDirection.ASC
