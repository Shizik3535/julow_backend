from __future__ import annotations

from app.context.notification.application.ports.notification.notification_sender_port import (
    NotificationSenderPort,
)
from app.context.notification.domain.events.notification_events import NotificationCreated
from app.context.notification.domain.value_objects.channel_type import ChannelType


async def on_notification_created_send(
    event: NotificationCreated,
    sender_port: NotificationSenderPort,
) -> None:
    """
    Обработчик доменного события NotificationCreated.

    Отправляет уведомление по каналам через NotificationSenderPort.
    SenderPort сам проверяет preferences и DND.
    """
    channels = [ch.value for ch in event.channels] if event.channels else [ChannelType.IN_APP.value]

    await sender_port.send_notification(
        recipient_id=event.recipient_id,
        notification_type=event.notification_type.value,
        title=event.title,
        body=event.body,
        data={
            "notification_id": event.notification_id,
            "priority": event.priority.value,
        },
        channels=channels,
        priority=event.priority.value,
    )
