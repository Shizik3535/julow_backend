from __future__ import annotations

from enum import Enum


class TimeReportPeriod(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"
