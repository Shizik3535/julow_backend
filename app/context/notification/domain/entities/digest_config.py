from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_entity import BaseEntity


@dataclass
class DigestConfig(BaseEntity):
    """
    Сущность настройки дайджеста уведомлений.

    Принадлежит агрегату NotificationPreferences.

    Атрибуты:
        is_enabled: Включён ли дайджест.
        frequency: Частота (daily/weekly).
        preferred_hour: Предпочитаемый час отправки (0-23).
    """

    is_enabled: bool = False
    frequency: str = "daily"
    preferred_hour: int = 9
