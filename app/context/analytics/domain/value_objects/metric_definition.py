from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.analytics.domain.value_objects.metric_aggregation import MetricAggregation


@dataclass(frozen=True)
class MetricDefinition(ValueObject):
    """Описание одной метрики: какое поле и как агрегировать.

    field=`*` используется для COUNT(*); alias — имя колонки в результате.
    """

    field: str = "*"
    aggregation: MetricAggregation = MetricAggregation.COUNT
    alias: str | None = None

    def __post_init__(self) -> None:
        if not self.field:
            raise ValidationException(field="metric_field", message="field обязателен")
        if self.field == "*" and self.aggregation != MetricAggregation.COUNT:
            raise ValidationException(
                field="metric_field",
                message=f"field='*' допустим только для COUNT, получено {self.aggregation.value}",
            )
