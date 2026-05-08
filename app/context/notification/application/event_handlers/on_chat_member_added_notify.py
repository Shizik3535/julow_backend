"""Обработчик события ``ChatMemberAdded`` (Communication BC).

Шлёт приглашённому пользователю уведомление о добавлении в чат.
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


class OnChatMemberAddedNotify(BaseEventHandler[dict[str, Any]]):
    """Шлёт уведомление пользователю, который был добавлен в чат."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "ChatMemberAdded":
            return
        payload = event.get("payload", {})
        chat_id = payload.get("chat_id", "")
        user_id = payload.get("user_id", "")
        if not chat_id or not user_id:
            return

        notification = Notification.create(
            recipient_id=Id.from_string(user_id),
            notification_type=NotificationType.CHAT_MEMBER_ADDED,
            title="Вас добавили в чат",
            body="Вас добавили участником чата.",
            priority=NotificationPriority.LOW,
            channels=[ChannelType.IN_APP],
            data={"chat_id": chat_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
