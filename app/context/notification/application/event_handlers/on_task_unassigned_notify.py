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


class OnTaskUnassignedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события TaskUnassigned из Task BC.

    Создаёт task_unassigned уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "TaskUnassigned":
            return

        payload = event.get("payload", {})
        task_id = payload.get("task_id", "")
        assignee_id_str = payload.get("assignee_id")
        if not assignee_id_str:
            return

        assignee_id = Id.from_string(assignee_id_str)
        notification = Notification.create(
            recipient_id=assignee_id,
            notification_type=NotificationType.TASK_UNASSIGNED,
            title="Снятие с задачи",
            body="Вы были сняты с задачи.",
            priority=NotificationPriority.LOW,
            channels=[ChannelType.IN_APP],
            data={"task_id": task_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
