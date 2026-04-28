from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope
from app.context.notification.domain.value_objects.digest_frequency import DigestFrequency


@dataclass(frozen=True)
class NotificationCreated(BaseDomainEvent):
    """Уведомление создано."""

    notification_id: str = ""
    recipient_id: str = ""
    notification_type: NotificationType = NotificationType.TASK_ASSIGNED
    title: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: list[ChannelType] = field(default_factory=list)


@dataclass(frozen=True)
class NotificationRead(BaseDomainEvent):
    """Уведомление прочитано."""

    notification_id: str = ""


@dataclass(frozen=True)
class AllNotificationsRead(BaseDomainEvent):
    """Все уведомления прочитаны."""

    user_id: str = ""
    workspace_id: str | None = None
    count: int = 0


@dataclass(frozen=True)
class NotificationArchived(BaseDomainEvent):
    """Уведомление архивировано."""

    notification_id: str = ""


@dataclass(frozen=True)
class NotificationPreferenceUpdated(BaseDomainEvent):
    """Настройка уведомлений обновлена."""

    user_id: str = ""
    notification_type: NotificationType = NotificationType.TASK_ASSIGNED
    channel: ChannelType = ChannelType.IN_APP
    enabled: bool = True
    scope: PreferenceScope = PreferenceScope.GLOBAL


@dataclass(frozen=True)
class DndSettingsUpdated(BaseDomainEvent):
    """DND обновлён."""

    user_id: str = ""
    enabled: bool = False


@dataclass(frozen=True)
class DigestSettingsUpdated(BaseDomainEvent):
    """Дайджест обновлён."""

    user_id: str = ""
    enabled: bool = False
    frequency: DigestFrequency = DigestFrequency.DAILY


@dataclass(frozen=True)
class DigestSent(BaseDomainEvent):
    """Дайджест отправлен."""

    user_id: str = ""
    notification_count: int = 0


@dataclass(frozen=True)
class DeviceTokenRegistered(BaseDomainEvent):
    """Токен устройства зарегистрирован."""

    user_id: str = ""
    platform: str = ""


@dataclass(frozen=True)
class DeviceTokenRemoved(BaseDomainEvent):
    """Токен устройства удалён/деактивирован."""

    user_id: str = ""
    platform: str = ""


@dataclass(frozen=True)
class ReminderWindowUpdated(BaseDomainEvent):
    """Окно напоминания обновлено."""

    user_id: str = ""
    hours: int = 24
