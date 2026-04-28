from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import NotificationPreferencesNotFoundException
from app.context.notification.application.dto.digest_settings_dto import DigestSettingsDTO


class GetDigestSettingsQuery(BaseQuery):
    """
    Запрос настроек дайджеста.

    Атрибуты:
        user_id: ID пользователя.
    """

    user_id: str


class GetDigestSettingsHandler(BaseQueryHandler[GetDigestSettingsQuery, DigestSettingsDTO]):
    """Обработчик запроса настроек дайджеста."""

    def __init__(self, preferences_repo: NotificationPreferencesRepository) -> None:
        super().__init__()
        self._repo = preferences_repo

    async def handle(self, query: GetDigestSettingsQuery) -> DigestSettingsDTO:
        user_id = Id.from_string(query.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(query.user_id)

        if preferences.digest_config is None:
            return DigestSettingsDTO()

        config = preferences.digest_config
        return DigestSettingsDTO(
            enabled=config.is_enabled,
            frequency=config.frequency.value,
            delivery_time=config.delivery_time.isoformat(),
            delivery_day=config.delivery_day,
            timezone=config.timezone,
        )
