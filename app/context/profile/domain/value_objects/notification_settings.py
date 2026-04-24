from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import BusinessRuleViolationException
from app.context.profile.domain.value_objects.type_preference import TypePreference
from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


def _default_type_preferences() -> list[TypePreference]:
    """Создаёт настройки уведомлений по умолчанию: все типы включены, IN_APP + EMAIL включены, PUSH + SMS выключены."""
    enabled_channels = [
        ChannelPreference(channel=NotificationChannel.IN_APP, is_enabled=True),
        ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=True),
        ChannelPreference(channel=NotificationChannel.PUSH, is_enabled=False),
        ChannelPreference(channel=NotificationChannel.SMS, is_enabled=False),
    ]
    return [
        TypePreference(notification_type=nt, channels=list(enabled_channels), is_enabled=True)
        for nt in NotificationType
    ]


@dataclass(frozen=True)
class NotificationSettings(ValueObject):
    """
    Группа настроек уведомлений.

    Инвариант: хотя бы один ChannelPreference включён
    для каждого TypePreference если is_enabled=True.

    Атрибуты:
        type_preferences: Список настроек по типам уведомлений.
    """

    type_preferences: list[TypePreference] = field(default_factory=_default_type_preferences)

    def __post_init__(self) -> None:
        for tp in self.type_preferences:
            if tp.is_enabled:
                has_enabled_channel = any(cp.is_enabled for cp in tp.channels)
                if not has_enabled_channel:
                    raise BusinessRuleViolationException(
                        rule="AtLeastOneEnabledChannel",
                        message=(
                            f"Тип уведомления {tp.notification_type.value} включён, "
                            f"но нет ни одного включённого канала доставки"
                        ),
                    )
