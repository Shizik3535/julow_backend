from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.inboard.task_participant_port import (
    TaskParticipantPort,
)
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.shared.application.messaging.domain_event_bus import DomainEventBus


class OnTaskDeadlineApproachingNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события TaskDeadlineApproaching из Task BC.

    Создаёт task_due_approaching уведомление для каждого исполнителя задачи.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        task_participant_port: TaskParticipantPort,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._task_participant_port = task_participant_port

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "TaskDeadlineApproaching":
            return

        payload = event.get("payload", {})
        task_id = payload.get("task_id", "")
        due_date = payload.get("due_date", "")
        if not task_id:
            return

        assignee_ids = await self._task_participant_port.get_task_assignees(task_id)
        if not assignee_ids:
            return

        for user_id in assignee_ids:
            # Дедупликация: не создавать повторное уведомление
            if await self._repo.has_unread_by_type_and_target(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.TASK_DUE_APPROACHING,
                target_key=task_id,
            ):
                continue

            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.TASK_DUE_APPROACHING,
                title="Приближение дедлайна",
                body="Дедлайн задачи приближается.",
                priority=NotificationPriority.NORMAL,
                channels=[ChannelType.IN_APP, ChannelType.EMAIL],
                data={"task_id": task_id, "due_date": due_date},
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
