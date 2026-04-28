from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.shared.application.messaging.domain_event_bus import DomainEventBus


class OnOrgInvitationSentNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события InvitationSent из Organization BC.

    Создаёт organization_invitation уведомление.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
        preferences_repo: NotificationPreferencesRepository,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus
        self._preferences_repo = preferences_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "InvitationSent":
            return

        payload = event.get("payload", {})
        org_id = payload.get("org_id", "")
        email = payload.get("email", "")
        role_id = payload.get("role_id", "")
        if not email:
            return

        # Для приглашений в организацию — уведомляем по email
        # Получатель неизвестен до принятия приглашения, отправляем на email
        notification = Notification.create(
            recipient_id=Id.generate(),  # placeholder, будет определён при принятии
            notification_type=NotificationType.ORGANIZATION_INVITATION,
            title="Приглашение в организацию",
            body=f"Вы получили приглашение в организацию.",
            priority=NotificationPriority.NORMAL,
            channels=[ChannelType.EMAIL],
            data={"org_id": org_id, "email": email, "role_id": role_id},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
