from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility


class UpdatePrivacyCommand(BaseCommand):
    """
    Команда обновления настроек приватности.

    Атрибуты:
        user_id: ID пользователя.
        profile_visibility: Видимость профиля (PUBLIC, ORGANIZATION_ONLY, PRIVATE).
        online_status_visibility: Видимость онлайн-статуса (EVERYONE, CONTACTS_ONLY, NOBODY).
        activity_tracking_consent: Согласие на отслеживание (GRANTED, DENIED).
    """

    user_id: str
    profile_visibility: str = "ORGANIZATION_ONLY"
    online_status_visibility: str = "EVERYONE"
    activity_tracking_consent: str = "GRANTED"


class UpdatePrivacyHandler(BaseCommandHandler[UpdatePrivacyCommand, None]):
    """
    Обработчик обновления настроек приватности.

    Создаёт VO PrivacySettings из входных данных,
    вызывает доменный метод update_privacy.
    """

    def __init__(self, profile_repo: UserProfileRepository, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdatePrivacyCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        settings = PrivacySettings(
            profile_visibility=ProfileVisibility(command.profile_visibility),
            online_status_visibility=OnlineStatusVisibility(command.online_status_visibility),
            activity_tracking_consent=ActivityTrackingConsent(command.activity_tracking_consent),
        )

        profile.update_privacy(settings)
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
