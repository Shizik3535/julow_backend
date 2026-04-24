from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel
from app.context.profile.domain.value_objects.notification_settings import NotificationSettings
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.domain.value_objects.type_preference import TypePreference


class TypePreferenceInput(BaseCommand):
    """
    Входные данные для одного типа уведомлений.

    Атрибуты:
        notification_type: Тип уведомления (например TASK_ASSIGNED).
        is_enabled: Включён ли данный тип.
        channels: Словарь {канал: включён}.
    """

    notification_type: str
    is_enabled: bool = True
    channels: dict[str, bool] = {}


class UpdateNotificationsCommand(BaseCommand):
    """
    Команда обновления настроек уведомлений.

    Атрибуты:
        user_id: ID пользователя.
        type_preferences: Список настроек по типам уведомлений.
    """

    user_id: str
    type_preferences: list[TypePreferenceInput]


class UpdateNotificationsHandler(BaseCommandHandler[UpdateNotificationsCommand, None]):
    """
    Обработчик обновления настроек уведомлений.

    Преобразует входные данные в доменные VO и вызывает
    update_notifications на агрегате.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateNotificationsCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        type_prefs: list[TypePreference] = []
        for tp_input in command.type_preferences:
            channels = [
                ChannelPreference(
                    channel=NotificationChannel(ch_name),
                    is_enabled=ch_enabled,
                )
                for ch_name, ch_enabled in tp_input.channels.items()
            ]
            type_prefs.append(
                TypePreference(
                    notification_type=NotificationType(tp_input.notification_type),
                    channels=channels,
                    is_enabled=tp_input.is_enabled,
                )
            )

        settings = NotificationSettings(type_preferences=type_prefs)
        profile.update_notifications(settings)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
