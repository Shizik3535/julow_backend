from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.analytics.domain.value_objects.time_granularity import TimeGranularity


@dataclass(frozen=True)
class Dimension(ValueObject):
    """Измерение группировки результатов аналитического запроса.

    Если задан time_granularity — поле трактуется как timestamp и группируется
    по соответствующему интервалу (для временных рядов).
    """

    field: str = ""
    time_granularity: TimeGranularity | None = None
    alias: str | None = None

    def __post_init__(self) -> None:
        if not self.field:
            raise ValidationException(field="dimension_field", message="field обязателен")
