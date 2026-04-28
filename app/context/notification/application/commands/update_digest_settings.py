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
    InvalidDigestConfigException,
)
from app.context.notification.domain.entities.digest_config import DigestConfig
from app.context.notification.domain.value_objects.digest_frequency import DigestFrequency


class UpdateDigestSettingsCommand(BaseCommand):
    """
    Команда обновления конфигурации дайджеста.

    Атрибуты:
        user_id: ID пользователя.
        enabled: Включён ли дайджест.
        frequency: Частота (daily/weekly).
        delivery_time: Время отправки (HH:MM).
        delivery_day: День отправки для weekly (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    user_id: str
    enabled: bool = False
    frequency: str = "daily"
    delivery_time: str = "09:00"
    delivery_day: int | None = None
    timezone: str = "UTC"


class UpdateDigestSettingsHandler(BaseCommandHandler[UpdateDigestSettingsCommand, None]):
    """Обработчик обновления конфигурации дайджеста."""

    def __init__(
        self,
        preferences_repo: NotificationPreferencesRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = preferences_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateDigestSettingsCommand) -> None:
        user_id = Id.from_string(command.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(command.user_id)

        try:
            delivery_time = time.fromisoformat(command.delivery_time)
        except ValueError:
            raise InvalidDigestConfigException("Некорректное время delivery_time")

        config = DigestConfig(
            is_enabled=command.enabled,
            frequency=DigestFrequency(command.frequency),
            delivery_time=delivery_time,
            delivery_day=command.delivery_day,
            timezone=command.timezone,
        )

        preferences.update_digest(config)
        await self._repo.update(preferences)
        await self._event_bus.publish_all(preferences.clear_domain_events())
