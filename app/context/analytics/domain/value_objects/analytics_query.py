from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.dimension import Dimension
from app.context.analytics.domain.value_objects.filter_config import FilterConfig
from app.context.analytics.domain.value_objects.metric_definition import MetricDefinition
from app.context.analytics.domain.value_objects.sort_config import SortConfig


@dataclass(frozen=True)
class AnalyticsQuery(ValueObject):
    """Единый кросс-BC запрос аналитики.

    Описывает что считать (metrics), как группировать (dimensions),
    откуда брать данные (data_source → bounded context), какие фильтры
    применить и за какой период. Резолвится на infrastructure-слое через ACL
    к соответствующему BC.

    Инварианты:
        - data_source обязателен;
        - либо хотя бы одна метрика, либо это «сырой» запрос (raw=True);
        - если задан date_range — он валиден (валидируется в DateRange).
    """

    data_source: DataSource = DataSource.TASKS
    metrics: list[MetricDefinition] = field(default_factory=list)
    dimensions: list[Dimension] = field(default_factory=list)
    filters: list[FilterConfig] = field(default_factory=list)
    date_range: DateRange | None = None
    sort: list[SortConfig] = field(default_factory=list)
    limit: int | None = None
    raw: bool = False

    def __post_init__(self) -> None:
        if not self.raw and not self.metrics:
            raise ValidationException(
                field="metrics",
                message="AnalyticsQuery должен содержать хотя бы одну метрику или быть raw=True",
            )
        if self.limit is not None and self.limit <= 0:
            raise ValidationException(field="limit", message=f"limit должен быть > 0: {self.limit}")

    @property
    def bounded_context(self) -> BoundedContextRef:
        return self.data_source.bounded_context

    @property
    def has_time_series(self) -> bool:
        return any(d.time_granularity is not None for d in self.dimensions)
