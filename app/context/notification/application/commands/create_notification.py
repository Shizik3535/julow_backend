from __future__ import annotations

from dataclasses import field

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.notification_priority import NotificationPriority
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.application.dto.notification_dto import NotificationDTO


class CreateNotificationCommand(BaseCommand):
    """
    Команда создания уведомления.

    Атрибуты:
        recipient_id: ID получателя.
        notification_type: Тип уведомления.
        title: Заголовок.
        body: Тело уведомления.
        priority: Приоритет.
        data: Контекстные данные.
        channels: Каналы доставки.
        workspace_id: ID workspace.
        actor_id: ID инициатора.
    """

    recipient_id: str
    notification_type: str
    title: str
    body: str
    priority: str = "normal"
    data: dict = field(default_factory=dict)
    channels: list[str] = field(default_factory=lambda: ["in_app"])
    workspace_id: str | None = None
    actor_id: str | None = None


class CreateNotificationHandler(BaseCommandHandler[CreateNotificationCommand, NotificationDTO]):
    """
    Обработчик создания уведомления.

    Создаёт агрегат Notification, сохраняет и публикует события.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateNotificationCommand) -> NotificationDTO:
        recipient_id = Id.from_string(command.recipient_id)
        workspace_id = Id.from_string(command.workspace_id) if command.workspace_id else None
        actor_id = Id.from_string(command.actor_id) if command.actor_id else None

        notification = Notification.create(
            recipient_id=recipient_id,
            notification_type=NotificationType(command.notification_type),
            title=command.title,
            body=command.body,
            priority=NotificationPriority(command.priority),
            data=command.data,
            channels=[ChannelType(ch) for ch in command.channels],
            workspace_id=workspace_id,
            actor_id=actor_id,
        )

        await self._repo.add(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())

        return NotificationDTO(
            id=str(notification.id),
            recipient_id=str(notification.recipient_id),
            workspace_id=str(notification.workspace_id) if notification.workspace_id else None,
            notification_type=notification.notification_type.value,
            title=notification.title,
            body=notification.body,
            priority=notification.priority.value,
            data=notification.data,
            channels=[ch.value for ch in notification.channels],
            is_read=notification.is_read,
            read_at=notification.read_at,
            is_archived=notification.is_archived,
            actor_id=str(notification.actor_id) if notification.actor_id else None,
            created_at=notification.created_at,
        )
