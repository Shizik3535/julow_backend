from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.dto.notification_preferences_dto import NotificationPreferencesDTO
from app.context.notification.application.dto.preference_entry_dto import PreferenceEntryDTO
from app.context.notification.application.ports.integration.outboard.notification_preferences_provider import (
    NotificationPreferencesProvider,
)
from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.infrastructure.persistence.repositories.sql_notification_preferences_repository import (
    SqlNotificationPreferencesRepository,
)


class NotificationPreferencesProviderAdapter(NotificationPreferencesProvider):
    """Реализация NotificationPreferencesProvider (outboard) — предоставляет настройки уведомлений другим BC."""

    def __init__(
        self,
        repo: NotificationPreferencesRepository,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self._repo = repo
        self._session_factory = session_factory

    def _make_repo(self, session: AsyncSession) -> NotificationPreferencesRepository:
        """Создаёт репозиторий с переданной сессией."""
        from app.context.notification.infrastructure.persistence.mappers.notification_preferences_mapper import (
            NotificationPreferencesMapper,
        )
        return SqlNotificationPreferencesRepository(
            session=session,
            mapper=NotificationPreferencesMapper(),
        )

    async def _load_aggregate(self, user_id: str) -> NotificationPreferences | None:
        """Загружает агрегат preferences, используя session_factory при наличии."""
        if self._session_factory is not None:
            async with self._session_factory() as session:
                repo = self._make_repo(session)
                return await repo.get_by_user_id(Id.from_string(user_id))
        return await self._repo.get_by_user_id(Id.from_string(user_id))

    async def get_preferences(self, user_id: str) -> NotificationPreferencesDTO | None:
        aggregate = await self._load_aggregate(user_id)
        if aggregate is None:
            return None

        from app.context.notification.domain.value_objects.channel_type import ChannelType
        from app.context.notification.domain.value_objects.notification_type import NotificationType
        from app.context.notification.domain.value_objects.preference_scope import PreferenceScope
        from app.context.notification.application.dto.project_override_dto import ProjectOverrideDTO

        # Группируем PreferenceEntry по notification_type + scope
        global_map: dict[str, dict[str, bool]] = {}
        project_map: dict[str, dict[str, dict[str, bool]]] = {}  # scope_id → {type → {channel → bool}}

        for entry in aggregate.preferences:
            ntype = entry.notification_type.value
            ch_key = entry.channel.value

            if entry.scope == PreferenceScope.GLOBAL:
                if ntype not in global_map:
                    global_map[ntype] = self._default_channels_for_type(aggregate, entry.notification_type)
                global_map[ntype][ch_key] = entry.enabled

            elif entry.scope in (PreferenceScope.PROJECT, PreferenceScope.WORKSPACE):
                scope_key = str(entry.scope_id) if entry.scope_id else ""
                if scope_key not in project_map:
                    project_map[scope_key] = {}
                if ntype not in project_map[scope_key]:
                    project_map[scope_key][ntype] = self._default_channels_for_type(aggregate, entry.notification_type)
                project_map[scope_key][ntype][ch_key] = entry.enabled

        global_prefs = [
            PreferenceEntryDTO(
                type=ntype,
                in_app=channels.get("in_app", True),
                email=channels.get("email", False),
                push=channels.get("push", False),
                webhook=channels.get("webhook", False),
            )
            for ntype, channels in global_map.items()
        ]

        project_overrides = [
            ProjectOverrideDTO(
                project_id=scope_id,
                preferences=[
                    PreferenceEntryDTO(
                        type=ntype,
                        in_app=channels.get("in_app", True),
                        email=channels.get("email", False),
                        push=channels.get("push", False),
                        webhook=channels.get("webhook", False),
                    )
                    for ntype, channels in type_entries.items()
                ],
            )
            for scope_id, type_entries in project_map.items()
        ]

        return NotificationPreferencesDTO(
            global_preferences=global_prefs,
            project_overrides=project_overrides,
        )

    def _default_channels_for_type(self, aggregate: NotificationPreferences, notification_type: NotificationType) -> dict[str, bool]:
        """Возвращает дефолтные каналы для типа из политики агрегата."""
        from app.context.notification.domain.value_objects.channel_type import ChannelType

        default_channels = aggregate.policy.get_default_channels(notification_type)
        return {
            ch.value: ch in default_channels
            for ch in ChannelType
        }

    async def should_deliver(self, user_id: str, notification_type: str, channel: str, scope_id: str | None = None) -> bool:
        aggregate = await self._load_aggregate(user_id)
        if aggregate is None:
            return True

        from app.context.notification.domain.value_objects.notification_type import NotificationType
        from app.context.notification.domain.value_objects.channel_type import ChannelType

        scope_id_vo = Id.from_string(scope_id) if scope_id else None
        return aggregate.should_deliver(
            NotificationType(notification_type),
            ChannelType(channel),
            scope_id_vo,
        )

    async def is_dnd_active(self, user_id: str) -> bool:
        aggregate = await self._load_aggregate(user_id)
        if aggregate is None:
            return False

        from datetime import datetime, timezone
        return aggregate.is_dnd_active(datetime.now(tz=timezone.utc))
