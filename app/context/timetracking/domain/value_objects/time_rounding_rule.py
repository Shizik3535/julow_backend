from __future__ import annotations

from enum import Enum


class TimeRoundingRule(Enum):
    """
    Правило округления времени.

    Новые правила = значение enum.

    Значения:
        NONE: Без округления
        ROUND_UP_15: Округление вверх до 15 минут
        ROUND_UP_30: Округление вверх до 30 минут
        ROUND_NEAREST_15: До ближайших 15 минут
        ROUND_NEAREST_30: До ближайших 30 минут
    """

    NONE = "none"
    ROUND_UP_15 = "round_up_15"
    ROUND_UP_30 = "round_up_30"
    ROUND_NEAREST_15 = "round_nearest_15"
    ROUND_NEAREST_30 = "round_nearest_30"
