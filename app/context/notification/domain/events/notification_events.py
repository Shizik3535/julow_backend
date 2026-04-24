from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.notification.domain.value_objects.notification_type import NotificationType


@dataclass(frozen=True)
class NotificationCreated(BaseDomainEvent):
    """Уведомление создано."""

    notification_id: str = ""
    recipient_id: str = ""
    notification_type: NotificationType = NotificationType.SYSTEM


@dataclass(frozen=True)
class NotificationRead(BaseDomainEvent):
    """Уведомление прочитано."""

    notification_id: str = ""


@dataclass(frozen=True)
class NotificationMarkedAllRead(BaseDomainEvent):
    """Все уведомления прочитаны."""

    user_id: str = ""


@dataclass(frozen=True)
class NotificationPreferencesUpdated(BaseDomainEvent):
    """Настройки уведомлений обновлены."""

    user_id: str = ""


@dataclass(frozen=True)
class DoNotDisturbEnabled(BaseDomainEvent):
    """DND включён."""

    user_id: str = ""


@dataclass(frozen=True)
class DoNotDisturbDisabled(BaseDomainEvent):
    """DND отключён."""

    user_id: str = ""


@dataclass(frozen=True)
class DigestSent(BaseDomainEvent):
    """Дайджест отправлен."""

    user_id: str = ""
