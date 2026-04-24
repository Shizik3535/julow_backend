from __future__ import annotations

from enum import Enum


class EffortUnit(Enum):
    """
    Единица оценки усилия.

    Новые единицы = значение enum.

    Значения:
        HOURS: Часы
        STORY_POINTS: Story points
        DAYS: Дни
        T_SHIRT: T-shirt размер
    """

    HOURS = "hours"
    STORY_POINTS = "story_points"
    DAYS = "days"
    T_SHIRT = "t_shirt"
