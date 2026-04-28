from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class DndSettingsDTO(BaseDTO):
    """
    DTO настроек DND.

    Атрибуты:
        enabled: Включён ли DND.
        schedule_start: Начало расписания (HH:MM).
        schedule_end: Конец расписания (HH:MM).
        schedule_days: Дни недели (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    enabled: bool = False
    schedule_start: str | None = None
    schedule_end: str | None = None
    schedule_days: list[int] | None = None
    timezone: str = "UTC"
