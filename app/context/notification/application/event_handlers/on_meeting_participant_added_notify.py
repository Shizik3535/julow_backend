"""Обработчик события ``MeetingParticipantAdded`` (Communication BC).

Отправляет пользователю уведомление-приглашение на совещание.
"""

from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.notification_priority import (
    NotificationPriority,
)
from app.context.notification.domain.value_objects.notification_type import (
    NotificationType,
)


class OnMeetingParticipantAddedNotify(BaseEventHandler[dict[str, Any]]):
    """Шлёт уведомление приглашённому участнику совещания."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "MeetingParticipantAdded":
            return
        payload = event.get("payload", {})
        meeting_id = payload.get("meeting_id", "")
        user_id = payload.get("user_id", "")
        if not meeting_id or not user_id:
            return

        notification = Notification.create(
            recipient_id=Id.from_string(user_id),
            notification_type=NotificationType.MEETING_SCHEDULED,
            title="Приглашение на совещание",
            body="Вас добавили участником совещания.",
            priority=NotificationPriority.MEDIUM,
            channels=[ChannelType.IN_APP],
            data={"meeting_id": meeting_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
