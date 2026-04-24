from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.timetracking.domain.value_objects.timer_state import TimerState


@dataclass
class TimeLog(BaseEntity):
    """
    Сущность записи старта/паузы/стопа таймера.

    Принадлежит агрегату TimeEntry.

    Атрибуты:
        action: Действие таймера.
        timestamp: Время действия.
        accumulated_seconds: Накопленное время на момент действия.
    """

    action: TimerState = TimerState.RUNNING
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    accumulated_seconds: int = 0
