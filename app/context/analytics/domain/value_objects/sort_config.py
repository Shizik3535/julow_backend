from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.analytics.domain.value_objects.sort_order import SortOrder


@dataclass(frozen=True)
class SortConfig(ValueObject):
    """Сортировка результатов аналитического запроса по полю/алиасу метрики."""

    field: str = ""
    order: SortOrder = SortOrder.DESC

    def __post_init__(self) -> None:
        if not self.field:
            raise ValidationException(field="sort_field", message="field обязателен")
