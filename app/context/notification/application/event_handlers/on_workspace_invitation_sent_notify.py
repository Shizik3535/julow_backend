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


class OnWorkspaceInvitationSentNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события InvitationSent из Workspace BC.

    Создаёт workspace_invitation уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "InvitationSent":
            return

        payload = event.get("payload", {})
        workspace_id = payload.get("workspace_id", "")
        email = payload.get("email", "")
        role_id = payload.get("role_id", "")
        if not email:
            return

        notification = Notification.create(
            recipient_id=Id.generate(),
            notification_type=NotificationType.WORKSPACE_INVITATION,
            title="Приглашение в workspace",
            body=f"Вы получили приглашение в workspace.",
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.IN_APP, ChannelType.EMAIL],
            data={"workspace_id": workspace_id, "email": email, "role_id": role_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
