"""Обработчик события ``MessageSent`` (Communication BC).

Шлёт IN_APP уведомление всем участникам чата кроме отправителя.
Системные сообщения (``message_type == "system"``) не нотифицируются.
"""

from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.inboard.chat_members_port import (
    ChatMembersPort,
)
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


class OnMessageSentNotify(BaseEventHandler[dict[str, Any]]):
    """Шлёт уведомления участникам чата (кроме отправителя) о новом сообщении."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        chat_members_port: ChatMembersPort,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._members_port = chat_members_port

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "MessageSent":
            return
        payload = event.get("payload", {})
        message_id = payload.get("message_id", "")
        chat_id = payload.get("chat_id", "")
        sender_id = payload.get("sender_id", "")
        message_type = payload.get("message_type", "text")
        if not message_id or not chat_id:
            return
        if message_type == "system":
            return

        member_ids = await self._members_port.get_chat_member_ids(chat_id)
        recipients = [uid for uid in member_ids if uid != sender_id]
        if not recipients:
            return

        for user_id in recipients:
            notification = Notification.create(
                recipient_id=Id.from_string(user_id),
                notification_type=NotificationType.CHAT_MESSAGE,
                title="Новое сообщение",
                body="В чате новое сообщение.",
                priority=NotificationPriority.LOW,
                channels=[ChannelType.IN_APP],
                data={"chat_id": chat_id, "message_id": message_id},
            )
            await self._repo.add(notification)
            await self._event_bus.publish_all(notification.clear_domain_events())
