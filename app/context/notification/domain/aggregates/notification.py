from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.notification_group_key import NotificationGroupKey
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.events.notification_events import NotificationCreated, NotificationRead, NotificationArchived


@dataclass
class Notification(AggregateRoot):
    """
    Корень агрегата уведомления (Notification BC).

    Атрибуты:
        recipient_id: ID получателя.
        workspace_id: ID workspace (opaque).
        notification_type: Тип уведомления.
        title: Заголовок.
        body: Тело уведомления.
        priority: Приоритет.
        data: Контекстные данные (task_id, project_id, etc.).
        channels: Каналы доставки.
        is_read: Прочитано ли.
        read_at: Время прочтения.
        is_archived: Архивировано ли.
        group_key: Ключ группировки.
        actor_id: ID инициатора (None для системных).
        created_at: Время создания.
    """

    recipient_id: Id = field(default_factory=Id.generate)
    workspace_id: Id | None = None
    notification_type: NotificationType = NotificationType.TASK_ASSIGNED
    title: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: dict[str, Any] = field(default_factory=dict)
    channels: list[ChannelType] = field(default_factory=list)
    is_read: bool = False
    read_at: datetime | None = None
    is_archived: bool = False
    group_key: NotificationGroupKey | None = None
    actor_id: Id | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        recipient_id: Id,
        notification_type: NotificationType,
        title: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: dict[str, Any] | None = None,
        channels: list[ChannelType] | None = None,
        workspace_id: Id | None = None,
        actor_id: Id | None = None,
        group_key: NotificationGroupKey | None = None,
    ) -> Notification:
        """Создаёт уведомление (unread)."""
        notification = cls(
            recipient_id=recipient_id,
            workspace_id=workspace_id,
            notification_type=notification_type,
            title=title,
            body=body,
            priority=priority,
            data=data or {},
            channels=channels or [ChannelType.IN_APP],
            actor_id=actor_id,
            group_key=group_key,
        )
        notification._register_event(
            NotificationCreated(
                notification_id=str(notification.id),
                recipient_id=str(recipient_id),
                notification_type=notification_type,
                title=title,
                body=body,
                priority=priority,
                channels=notification.channels,
            )
        )
        return notification

    def mark_read(self) -> None:
        """Помечает уведомление как прочитанное. Идемпотентно — повторный вызов не вызывает ошибку."""
        if self.is_read:
            return
        self.is_read = True
        self.read_at = datetime.now(tz=timezone.utc)
        self._register_event(NotificationRead(notification_id=str(self.id)))

    def archive(self) -> None:
        """Архивирует уведомление."""
        if self.is_archived:
            return
        self.is_archived = True
        self._register_event(NotificationArchived(notification_id=str(self.id)))
