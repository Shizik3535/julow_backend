from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope


@dataclass
class PreferenceEntry(BaseEntity):
    """
    Сущность записи настройки уведомлений.

    Принадлежит агрегату NotificationPreferences.

    Атрибуты:
        notification_type: Тип уведомления.
        channel: Канал доставки.
        enabled: Включён ли канал для данного типа.
        scope: Область действия (global/project/workspace).
        scope_id: ID проекта или workspace (для project/workspace scope).
    """

    notification_type: NotificationType = NotificationType.TASK_ASSIGNED
    channel: ChannelType = ChannelType.IN_APP
    enabled: bool = True
    scope: PreferenceScope = PreferenceScope.GLOBAL
    scope_id: Id | None = None
