from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.domain.value_objects.channel_preference import ChannelPreference


@dataclass(frozen=True)
class TypePreference(ValueObject):
    """
    Настройка типа уведомления с каналами доставки.

    Атрибуты:
        notification_type: Тип уведомления.
        channels: Список настроек каналов для данного типа.
        is_enabled: Включён ли тип уведомления целиком.
    """

    notification_type: NotificationType = NotificationType.TASK_ASSIGNED
    channels: list[ChannelPreference] = field(default_factory=list)
    is_enabled: bool = True
