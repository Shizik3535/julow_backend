from __future__ import annotations

from enum import Enum


class MetricAggregation(Enum):
    """Тип агрегации значения метрики."""

    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"
    RATE = "rate"
