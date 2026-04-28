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


class OnAuthFactorChangedNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик событий AuthFactorEnabled/AuthFactorDisabled из Identity BC.

    Создаёт security_2fa_changed уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type not in ("AuthFactorEnabled", "AuthFactorDisabled"):
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        method = payload.get("method", "")
        if not user_id_str:
            return

        user_id = Id.from_string(user_id_str)
        action = "включён" if event_type == "AuthFactorEnabled" else "отключён"
        notification = Notification.create(
            recipient_id=user_id,
            notification_type=NotificationType.SECURITY_2FA_CHANGED,
            title="Изменение двухфакторной аутентификации",
            body=f"Фактор аутентификации {method} был {action}.",
            priority=NotificationPriority.HIGH,
            channels=[ChannelType.EMAIL],
            data={"method": method, "action": action},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
