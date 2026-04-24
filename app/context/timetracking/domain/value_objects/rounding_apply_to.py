from __future__ import annotations

from enum import Enum


class RoundingApplyTo(Enum):
    """
    К каким записям применять округление.

    Значения:
        TIMER_ONLY: Только таймер
        MANUAL_ONLY: Только ручной ввод
        ALL: Ко всем
    """

    TIMER_ONLY = "timer_only"
    MANUAL_ONLY = "manual_only"
    ALL = "all"
