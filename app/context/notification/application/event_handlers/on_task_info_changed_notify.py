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


class OnTaskInfoChangedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события TaskInfoChanged из Task BC.

    Если changed_fields содержит "due_date", создаёт
    task_deadline_changed уведомление для каждого участника задачи.
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
        if event_type != "TaskInfoChanged":
            return

        payload = event.get("payload", {})
        task_id = payload.get("task_id", "")
        changed_fields: list[str] = payload.get("changed_fields", [])
        if not task_id:
            return

        if "due_date" not in changed_fields:
            return

        participant_ids = await self._task_participant_port.get_task_participants(task_id)
        if not participant_ids:
            return

        for user_id in participant_ids:
            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.TASK_DEADLINE_CHANGED,
                title="Изменение сроков задачи",
                body="Сроки выполнения задачи были изменены.",
                priority=NotificationPriority.NORMAL,
                channels=[ChannelType.IN_APP, ChannelType.EMAIL],
                data={"task_id": task_id},
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
