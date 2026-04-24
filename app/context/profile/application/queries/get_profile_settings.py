from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.application.dto.profile_settings_dto import ProfileSettingsDTO
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository


class GetProfileSettingsQuery(BaseQuery):
    """
    Запрос настроек профиля по user_id.

    Атрибуты:
        user_id: Идентификатор пользователя (из Identity BC).
    """

    user_id: str


class GetProfileSettingsHandler(BaseQueryHandler[GetProfileSettingsQuery, ProfileSettingsDTO]):
    """
    Обработчик запроса настроек профиля.

    Загружает профиль по user_id и преобразует настройки в ProfileSettingsDTO.
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        super().__init__()
        self._profile_repo = profile_repo

    async def handle(self, query: GetProfileSettingsQuery) -> ProfileSettingsDTO:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(query.user_id))
        if profile is None:
            raise ProfileNotFoundException(query.user_id)

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
