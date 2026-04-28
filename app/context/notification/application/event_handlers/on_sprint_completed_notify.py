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


class OnSprintCompletedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события SprintCompleted из Project BC.

    Создаёт sprint_completed уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "SprintCompleted":
            return

        payload = event.get("payload", {})
        sprint_id = payload.get("sprint_id", "")
        if not sprint_id:
            return

        notification = Notification.create(
            recipient_id=Id.generate(),
            notification_type=NotificationType.SPRINT_COMPLETED,
            title="Спринт завершён",
            body="Спринт завершён.",
            priority=NotificationPriority.LOW,
            channels=[ChannelType.IN_APP],
            data={"sprint_id": sprint_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
