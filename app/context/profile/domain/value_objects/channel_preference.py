from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


@dataclass(frozen=True)
class ChannelPreference(ValueObject):
    """
    Настройка канала доставки для типа уведомления.

    Атрибуты:
        channel: Канал доставки.
        is_enabled: Включён ли канал.
    """

    channel: NotificationChannel = NotificationChannel.IN_APP
    is_enabled: bool = True
