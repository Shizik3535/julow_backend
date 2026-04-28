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


class OnTaskStatusChangedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события TaskStatusChanged из Task BC.

    Создаёт task_status_changed уведомление для каждого участника задачи.
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
        if event_type != "TaskStatusChanged":
            return

        payload = event.get("payload", {})
        task_id = payload.get("task_id", "")
        old_status_id = payload.get("old_status_id", "")
        new_status_id = payload.get("new_status_id", "")
        changed_by = payload.get("changed_by") or payload.get("actor_id")
        if not task_id:
            return

        participant_ids = await self._task_participant_port.get_task_participants(task_id)
        if not participant_ids:
            return

        # Не уведомлять пользователя, инициировавшего изменение
        recipients = [uid for uid in participant_ids if uid != changed_by]

        for user_id in recipients:
            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.TASK_STATUS_CHANGED,
                title="Изменение статуса задачи",
                body="Статус задачи изменён.",
                priority=NotificationPriority.LOW,
                channels=[ChannelType.IN_APP],
                data={"task_id": task_id, "old_status_id": old_status_id, "new_status_id": new_status_id},
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
