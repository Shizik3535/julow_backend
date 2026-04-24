from __future__ import annotations

from enum import Enum


class ViewType(Enum):
    """
    Тип представления проекта.

    Значения:
        BOARD: Доска
        LIST: Список
        TIMELINE: Таймлайн
        CALENDAR: Календарь
        TABLE: Таблица
        ACTIVITY: Активность
    """

    BOARD = "board"
    LIST = "list"
    TIMELINE = "timeline"
    CALENDAR = "calendar"
    TABLE = "table"
    ACTIVITY = "activity"
