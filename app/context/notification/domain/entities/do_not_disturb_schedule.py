from __future__ import annotations

import zoneinfo
from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from typing import Sequence

from app.shared.domain.base_entity import BaseEntity
from app.context.notification.domain.exceptions.notification_exceptions import InvalidDndScheduleException


@dataclass
class DoNotDisturbSchedule(BaseEntity):
    """
    Сущность расписания «Не беспокоить».

    Принадлежит агрегату NotificationPreferences.

    Атрибуты:
        enabled: Включён ли DND.
        schedule_start: Начало расписания (часы).
        schedule_end: Конец расписания (часы).
        schedule_days: Дни недели (0=Пн, 6=Вс). None = каждый день.
        timezone: Часовой пояс.
    """

    enabled: bool = False
    schedule_start: time | None = None
    schedule_end: time | None = None
    schedule_days: list[int] | None = None
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        if self.schedule_days is not None:
            for day in self.schedule_days:
                if not (0 <= day <= 6):
                    raise InvalidDndScheduleException(f"schedule_days содержит недопустимое значение {day}; допустимы 0–6")
        if self.enabled and self.schedule_start is None and self.schedule_end is None:
            raise InvalidDndScheduleException("DND включён, но не указано расписание (schedule_start/schedule_end)")
        try:
            zoneinfo.ZoneInfo(self.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise InvalidDndScheduleException(f"Недопустимый часовой пояс: {self.timezone}")

    def is_active_at(self, now: datetime) -> bool:
        """Проверяет, попадает ли момент в расписание DND."""
        if not self.enabled:
            return False
        if self.schedule_start is None or self.schedule_end is None:
            # Safety fallback — валидация не должна допускать этого при enabled=True
            return False

        tz = zoneinfo.ZoneInfo(self.timezone)

        local_now = now.astimezone(tz)
        current_time = local_now.time()
        current_day = local_now.weekday()

        if self.schedule_days is not None and current_day not in self.schedule_days:
            return False

        if self.schedule_start <= self.schedule_end:
            return self.schedule_start <= current_time <= self.schedule_end
        else:
            return current_time >= self.schedule_start or current_time <= self.schedule_end
