from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.exceptions.notification_exceptions import NotificationPreferencesNotFoundException
from app.context.notification.domain.value_objects.channel_type import ChannelType
from app.context.notification.domain.value_objects.preference_scope import PreferenceScope
from app.context.notification.application.dto.notification_preferences_dto import NotificationPreferencesDTO
from app.context.notification.application.dto.preference_entry_dto import PreferenceEntryDTO
from app.context.notification.application.dto.project_override_dto import ProjectOverrideDTO


class GetNotificationPreferencesQuery(BaseQuery):
    """
    Запрос настроек уведомлений.

    Атрибуты:
        user_id: ID пользователя.
    """

    user_id: str


class GetNotificationPreferencesHandler(
    BaseQueryHandler[GetNotificationPreferencesQuery, NotificationPreferencesDTO]
):
    """Обработчик запроса настроек уведомлений."""

    def __init__(self, preferences_repo: NotificationPreferencesRepository) -> None:
        super().__init__()
        self._repo = preferences_repo

    async def handle(self, query: GetNotificationPreferencesQuery) -> NotificationPreferencesDTO:
        user_id = Id.from_string(query.user_id)
        preferences = await self._repo.get_by_user_id(user_id)
        if preferences is None:
            raise NotificationPreferencesNotFoundException(query.user_id)

        # Группируем глобальные настройки по типу
        global_by_type: dict[str, dict[str, bool]] = {}
        for entry in preferences.preferences:
            if entry.scope == PreferenceScope.GLOBAL:
                if entry.notification_type.value not in global_by_type:
                    global_by_type[entry.notification_type.value] = {}
                global_by_type[entry.notification_type.value][entry.channel.value] = entry.enabled

        global_preferences = [
            PreferenceEntryDTO(
                type=ntype,
                in_app=channels.get("in_app", False),
                email=channels.get("email", False),
                push=channels.get("push", False),
            )
            for ntype, channels in global_by_type.items()
        ]

        # Группируем project overrides
        project_map: dict[str, dict[str, dict[str, bool]]] = {}
        for entry in preferences.preferences:
            if entry.scope == PreferenceScope.PROJECT and entry.scope_id is not None:
                pid = str(entry.scope_id)
                if pid not in project_map:
                    project_map[pid] = {}
                if entry.notification_type.value not in project_map[pid]:
                    project_map[pid][entry.notification_type.value] = {}
                project_map[pid][entry.notification_type.value][entry.channel.value] = entry.enabled

        project_overrides = [
            ProjectOverrideDTO(
                project_id=pid,
                preferences=[
                    PreferenceEntryDTO(
                        type=ntype,
                        in_app=channels.get("in_app", False),
                        email=channels.get("email", False),
                        push=channels.get("push", False),
                    )
                    for ntype, channels in type_map.items()
                ],
            )
            for pid, type_map in project_map.items()
        ]

        return NotificationPreferencesDTO(
            global_preferences=global_preferences,
            project_overrides=project_overrides,
            reminder_window_hours=preferences.reminder_window_hours,
        )
