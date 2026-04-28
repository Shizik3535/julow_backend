from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.domain.events.notification_events import AllNotificationsRead


class MarkAllNotificationsReadCommand(BaseCommand):
    """
    Команда пометки всех уведомлений как прочитанных.

    Атрибуты:
        user_id: ID пользователя.
        workspace_id: ID workspace (опционально).
    """

    user_id: str
    workspace_id: str | None = None


class MarkAllNotificationsReadHandler(BaseCommandHandler[MarkAllNotificationsReadCommand, int]):
    """Обработчик пометки всех уведомлений как прочитанных. Возвращает количество."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, command: MarkAllNotificationsReadCommand) -> int:
        user_id = Id.from_string(command.user_id)
        workspace_id = Id.from_string(command.workspace_id) if command.workspace_id else None
        count = await self._repo.mark_all_read(user_id, workspace_id)
        if count > 0:
            await self._event_bus.publish_all([
                AllNotificationsRead(
                    user_id=command.user_id,
                    workspace_id=command.workspace_id,
                    count=count,
                )
            ])
        return count
