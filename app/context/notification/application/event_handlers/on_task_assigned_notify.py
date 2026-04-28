from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.shared.application.messaging.domain_event_bus import DomainEventBus


class OnTaskAssignedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события TaskAssigned из Task BC.

    Создаёт task_assigned уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "TaskAssigned":
            return

        payload = event.get("payload", {})
        task_id = payload.get("task_id", "")
        assignee_id_str = payload.get("assignee_id")
        if not assignee_id_str:
            return

        assignee_id = Id.from_string(assignee_id_str)
        notification = Notification.create(
            recipient_id=assignee_id,
            notification_type=NotificationType.TASK_ASSIGNED,
            title="Назначение на задачу",
            body="Вам была назначена задача.",
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.IN_APP, ChannelType.EMAIL],
            data={"task_id": task_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
