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


class OnNewDeviceLoginNotify(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события NewDeviceLogin из Identity BC.

    Создаёт security_new_device уведомление.
    """

    def __init__(self, notification_repo: NotificationRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "NewDeviceLogin":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        ip = payload.get("ip", "неизвестный IP")
        device = payload.get("device", "неизвестное устройство")
        if not user_id_str:
            return

        user_id = Id.from_string(user_id_str)
        notification = Notification.create(
            recipient_id=user_id,
            notification_type=NotificationType.SECURITY_NEW_DEVICE,
            title="Вход с нового устройства",
            body=f"Обнаружен вход с нового устройства: {device} ({ip}).",
            priority=NotificationPriority.HIGH,
            channels=[ChannelType.EMAIL],
            data={"ip": ip, "device": device},
        )
        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
