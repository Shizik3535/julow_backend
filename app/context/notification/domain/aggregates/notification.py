from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.notification_group_key import NotificationGroupKey
from app.context.notification.domain.events.notification_events import NotificationCreated, NotificationRead


@dataclass
class Notification(AggregateRoot):
    """
    Корень агрегата уведомления (Notification BC).

    Атрибуты:
        recipient_id: ID получателя.
        notification_type: Тип уведомления.
        title: Заголовок.
        body: Тело уведомления.
        priority: Приоритет.
        is_read: Прочитано ли.
        group_key: Ключ группировки.
        source_type: Тип источника (task, comment, meeting, etc.).
        source_id: Opaque ID источника.
        action_url: URL действия.
        created_at: Время создания.
    """

    recipient_id: Id = field(default_factory=Id.generate)
    notification_type: NotificationType = NotificationType.SYSTEM
    title: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.MEDIUM
    is_read: bool = False
    group_key: NotificationGroupKey | None = None
    source_type: str | None = None
    source_id: Id | None = None
    action_url: Url | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        recipient_id: Id,
        notification_type: NotificationType,
        title: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        source_type: str | None = None,
        source_id: Id | None = None,
        action_url: Url | None = None,
        group_key: NotificationGroupKey | None = None,
    ) -> Notification:
        """Создаёт уведомление (unread)."""
        notification = cls(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            body=body,
            priority=priority,
            source_type=source_type,
            source_id=source_id,
            action_url=action_url,
            group_key=group_key,
        )
        notification._register_event(
            NotificationCreated(
                notification_id=str(notification.id),
                recipient_id=str(recipient_id),
                notification_type=notification_type,
            )
        )
        return notification

    def mark_read(self) -> None:
        """Помечает уведомление как прочитанное."""
        if self.is_read:
            return
        self.is_read = True
        self._register_event(NotificationRead(notification_id=str(self.id)))
