from __future__ import annotations

from enum import Enum


class WeekStartDay(Enum):
    """
    День начала недели.

    Значения:
        MONDAY: Понедельник (ISO 8601).
        SUNDAY: Воскресенье.
        SATURDAY: Суббота.
    """

    MONDAY = "monday"
    SUNDAY = "sunday"
    SATURDAY = "saturday"
