from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import NotificationPreferencesNotFoundException
from app.context.notification.domain.value_objects.notification_type import NotificationType
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope


class SetNotificationPreferenceCommand(BaseCommand):
    """
    Команда установки настройки уведомлений.

    Атрибуты:
        user_id: ID пользователя.
        notification_type: Тип уведомления.
        channel: Канал доставки.
        enabled: Включён ли канал.
        scope: Область действия (global/project/workspace).
        scope_id: ID проекта или workspace.
    """

    user_id: str
    notification_type: str
    channel: str
    enabled: bool = True
    scope: str = "global"
    scope_id: str | None = None


class SetNotificationPreferenceHandler(BaseCommandHandler[SetNotificationPreferenceCommand, None]):
    """Обработчик установки настройки уведомлений."""

    def __init__(
        self,
        preferences_repo: NotificationPreferencesRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = preferences_repo
        self._event_bus = event_bus

    async def handle(self, command: SetNotificationPreferenceCommand) -> None:
        user_id = Id.from_string(command.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(command.user_id)

        scope_id = Id.from_string(command.scope_id) if command.scope_id else None

        preferences.set_preference(
            notification_type=NotificationType(command.notification_type),
            channel=ChannelType(command.channel),
            enabled=command.enabled,
            scope=PreferenceScope(command.scope),
            scope_id=scope_id,
        )

        await self._repo.update(preferences)
        await self._event_bus.publish_all(preferences.clear_domain_events())
