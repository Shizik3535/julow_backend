from __future__ import annotations

from datetime import date
from typing import Any

from app.shared.application.base_dto import BaseDTO


class FilterConfigDTO(BaseDTO):
    """DTO одного фильтра аналитического запроса."""

    field: str
    operator: str  # FilterOperator.value
    value: str
    value_to: str | None = None


class MetricDefinitionDTO(BaseDTO):
    """DTO описания метрики."""

    field: str = "*"
    aggregation: str = "count"  # MetricAggregation.value
    alias: str | None = None


class DimensionDTO(BaseDTO):
    """DTO измерения группировки."""

    field: str
    time_granularity: str | None = None  # TimeGranularity.value
    alias: str | None = None


class SortConfigDTO(BaseDTO):
    """DTO правила сортировки."""

    field: str
    order: str = "desc"  # SortOrder.value


class DateRangeDTO(BaseDTO):
    """DTO диапазона дат (включительно)."""

    start: date | None = None
    end: date | None = None


class AnalyticsQueryDTO(BaseDTO):
    """DTO аналитического запроса (плоский для API/persistence)."""

    data_source: str  # DataSource.value
    metrics: list[MetricDefinitionDTO] = []
    dimensions: list[DimensionDTO] = []
    filters: list[FilterConfigDTO] = []
    date_range: DateRangeDTO | None = None
    sort: list[SortConfigDTO] = []
    limit: int | None = None
    raw: bool = False


class AnalyticsResultRowDTO(BaseDTO):
    """Одна строка результата (имена колонок = aliases метрик/измерений)."""

    values: dict[str, Any] = {}


class AnalyticsResultDTO(BaseDTO):
    """Результат выполнения AnalyticsQuery (для виджетов и отчётов)."""

    data_source: str
    bounded_context: str  # BoundedContextRef.value
    columns: list[str] = []
    rows: list[AnalyticsResultRowDTO] = []
    total: int = 0
    generated_at: str = ""  # ISO datetime
