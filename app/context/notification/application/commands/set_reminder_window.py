from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import NotificationPreferencesNotFoundException


class SetReminderWindowCommand(BaseCommand):
    """
    Команда установки окна напоминания о дедлайне.

    Аргументы:
        user_id: ID пользователя.
        hours: Окно напоминания в часах (1–168).
    """

    user_id: str
    hours: int = 24


class SetReminderWindowHandler(BaseCommandHandler[SetReminderWindowCommand, None]):
    """Обработчик установки окна напоминания."""

    def __init__(
        self,
        preferences_repo: NotificationPreferencesRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = preferences_repo
        self._event_bus = event_bus

    async def handle(self, command: SetReminderWindowCommand) -> None:
        user_id = Id.from_string(command.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(command.user_id)

        preferences.set_reminder_window(command.hours)

        await self._repo.update(preferences)
        await self._event_bus.publish_all(preferences.clear_domain_events())
