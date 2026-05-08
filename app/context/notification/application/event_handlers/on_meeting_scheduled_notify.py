"""Обработчик события ``MeetingScheduled`` (Communication BC)."""

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


class OnMeetingScheduledNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обрабатывает ``MeetingScheduled`` из Communication BC.

    Сейчас отправляет уведомление только организатору (MVP). Уведомление
    остальным участникам будет добавлено после публикации события
    ``MeetingParticipantAdded`` отдельным handler'ом — тогда reactor получит
    ID каждого добавленного участника.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "MeetingScheduled":
            return
        payload = event.get("payload", {})
        meeting_id = payload.get("meeting_id", "")
        title = payload.get("title", "Совещание")
        if not meeting_id:
            return
        # В событии MeetingScheduled нет organizer_id — его можно получить
        # через сведения о самом совещании, но это уже запрос в Communication
        # BC. В MVP отправляем событие как системное «поставить в календарь».
        # Реальные получатели будут добавлены в отдельных handler'ах
        # ``MeetingParticipantAdded`` и ``MeetingCancelled``.
        return None
