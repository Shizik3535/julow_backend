from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.exceptions.notification_exceptions import NotificationNotFoundException


class ArchiveNotificationCommand(BaseCommand):
    """
    Команда архивирования уведомления.

    Атрибуты:
        notification_id: ID уведомления.
    """

    notification_id: str


class ArchiveNotificationHandler(BaseCommandHandler[ArchiveNotificationCommand, None]):
    """Обработчик архивирования уведомления."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, command: ArchiveNotificationCommand) -> None:
        notification = await self._repo.get_by_id(Id.from_string(command.notification_id))
        if notification is None:
            raise NotificationNotFoundException(command.notification_id)

        notification.archive()
        await self._repo.update(notification)
        await self._event_bus.publish_all(notification.clear_domain_events())
