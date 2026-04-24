from __future__ import annotations

from enum import Enum


class TimeFormat(Enum):
    """
    Формат отображения времени.

    Значения:
        H24: 24-часовой формат (14:30).
        H12: 12-часовой формат (2:30 PM).
    """

    H24 = "h24"
    H12 = "h12"
