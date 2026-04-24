from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_entity import BaseEntity


@dataclass
class DoNotDisturbSchedule(BaseEntity):
    """
    Сущность расписания «Не беспокоить».

    Принадлежит агрегату NotificationPreferences.

    Атрибуты:
        start_hour: Час начала (0-23).
        start_minute: Минута начала (0-59).
        end_hour: Час окончания (0-23).
        end_minute: Минута окончания (0-59).
        enabled: Включено ли расписание.
    """

    start_hour: int = 22
    start_minute: int = 0
    end_hour: int = 8
    end_minute: int = 0
    enabled: bool = True
