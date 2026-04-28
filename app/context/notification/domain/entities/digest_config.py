from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from app.shared.domain.base_entity import BaseEntity
from app.context.notification.domain.value_objects.digest_frequency import DigestFrequency
from app.context.notification.domain.exceptions.notification_exceptions import InvalidDigestConfigException


@dataclass
class DigestConfig(BaseEntity):
    """
    Сущность настройки дайджеста уведомлений.

    Принадлежит агрегату NotificationPreferences.

    Атрибуты:
        is_enabled: Включён ли дайджест.
        frequency: Частота (daily/weekly).
        delivery_time: Время отправки.
        delivery_day: День отправки для weekly (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    is_enabled: bool = False
    frequency: DigestFrequency = DigestFrequency.DAILY
    delivery_time: time = time(9, 0)
    delivery_day: int | None = None
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        if self.is_enabled and self.frequency == DigestFrequency.WEEKLY and self.delivery_day is None:
            raise InvalidDigestConfigException("При weekly частоте delivery_day обязателен (0–6)")
        if self.is_enabled and self.delivery_day is not None and not (0 <= self.delivery_day <= 6):
            raise InvalidDigestConfigException("delivery_day должен быть в диапазоне 0–6")
