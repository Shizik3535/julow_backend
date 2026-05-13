from __future__ import annotations

from enum import Enum


class TimeGranularity(Enum):
    """Гранулярность группировки по времени (для временных рядов)."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
