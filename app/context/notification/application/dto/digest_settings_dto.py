from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class DigestSettingsDTO(BaseDTO):
    """
    DTO настроек дайджеста.

    Атрибуты:
        enabled: Включён ли дайджест.
        frequency: Частота (daily/weekly).
        delivery_time: Время отправки (HH:MM).
        delivery_day: День отправки для weekly.
        timezone: Часовой пояс.
    """

    enabled: bool = False
    frequency: str = "daily"
    delivery_time: str = "09:00"
    delivery_day: int | None = None
    timezone: str = "UTC"
