from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import NotificationPreferencesNotFoundException
from app.context.notification.application.dto.dnd_settings_dto import DndSettingsDTO


class GetDndSettingsQuery(BaseQuery):
    """
    Запрос настроек DND.

    Атрибуты:
        user_id: ID пользователя.
    """

    user_id: str


class GetDndSettingsHandler(BaseQueryHandler[GetDndSettingsQuery, DndSettingsDTO]):
    """Обработчик запроса настроек DND."""

    def __init__(self, preferences_repo: NotificationPreferencesRepository) -> None:
        super().__init__()
        self._repo = preferences_repo

    async def handle(self, query: GetDndSettingsQuery) -> DndSettingsDTO:
        user_id = Id.from_string(query.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(query.user_id)

        if preferences.dnd_schedule is None:
            return DndSettingsDTO()

        schedule = preferences.dnd_schedule
        return DndSettingsDTO(
            enabled=schedule.enabled,
            schedule_start=schedule.schedule_start.isoformat() if schedule.schedule_start else None,
            schedule_end=schedule.schedule_end.isoformat() if schedule.schedule_end else None,
            schedule_days=schedule.schedule_days,
            timezone=schedule.timezone,
        )
