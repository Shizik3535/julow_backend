from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.dto.profile_settings_dto import ProfileSettingsDTO
from app.context.profile.application.ports.integration.outboard.profile_settings_provider import (
    ProfileSettingsProvider,
)
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class ProfileSettingsProviderAdapter(ProfileSettingsProvider):
    """
    Реализация ProfileSettingsProvider.

    Предоставляет настройки профиля (локализация, приватность)
    другим BC через синхронный DI-порт.
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def get_settings(self, user_id: str) -> ProfileSettingsDTO | None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(user_id))
        if profile is None:
            return None
        return ProfileSettingsDTO(
            user_id=str(profile.user_id),
            language=str(profile.localization.language),
            timezone=str(profile.localization.timezone),
            date_format=str(profile.localization.date_format),
            time_format=profile.localization.time_format.value,
            week_start_day=profile.localization.week_start_day.value,
            profile_visibility=profile.privacy.profile_visibility.value,
            online_status_visibility=profile.privacy.online_status_visibility.value,
            activity_tracking_consent=profile.privacy.activity_tracking_consent.value,
        )
