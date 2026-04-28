from __future__ import annotations

from datetime import time

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import (
    NotificationPreferencesNotFoundException,
    InvalidDndScheduleException,
)
from app.context.notification.domain.entities.do_not_disturb_schedule import DoNotDisturbSchedule


class UpdateDndSettingsCommand(BaseCommand):
    """
    Команда обновления расписания DND.

    Атрибуты:
        user_id: ID пользователя.
        enabled: Включён ли DND.
        schedule_start: Начало расписания (HH:MM).
        schedule_end: Конец расписания (HH:MM).
        schedule_days: Дни недели (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    user_id: str
    enabled: bool = False
    schedule_start: str | None = None
    schedule_end: str | None = None
    schedule_days: list[int] | None = None
    timezone: str = "UTC"


class UpdateDndSettingsHandler(BaseCommandHandler[UpdateDndSettingsCommand, None]):
    """Обработчик обновления расписания DND."""

    def __init__(
        self,
        preferences_repo: NotificationPreferencesRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = preferences_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateDndSettingsCommand) -> None:
        user_id = Id.from_string(command.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(command.user_id)

        schedule_start = None
        schedule_end = None
        if command.schedule_start:
            try:
                schedule_start = time.fromisoformat(command.schedule_start)
            except ValueError:
                raise InvalidDndScheduleException("Некорректное время schedule_start")
        if command.schedule_end:
            try:
                schedule_end = time.fromisoformat(command.schedule_end)
            except ValueError:
                raise InvalidDndScheduleException("Некорректное время schedule_end")

        schedule = DoNotDisturbSchedule(
            enabled=command.enabled,
            schedule_start=schedule_start,
            schedule_end=schedule_end,
            schedule_days=command.schedule_days,
            timezone=command.timezone,
        )

        preferences.update_dnd(schedule)
        await self._repo.update(preferences)
        await self._event_bus.publish_all(preferences.clear_domain_events())
