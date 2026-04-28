from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.application.ports.integration.outboard.reminder_window_provider import (
    ReminderWindowProvider,
)
from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.infrastructure.persistence.repositories.sql_notification_preferences_repository import (
    SqlNotificationPreferencesRepository,
)


class ReminderWindowProviderAdapter(ReminderWindowProvider):
    """Реализация ReminderWindowProvider (outboard) — предоставляет окно напоминания другим BC."""

    def __init__(
        self,
        repo: NotificationPreferencesRepository,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self._repo = repo
        self._session_factory = session_factory

    def _make_repo(self, session: AsyncSession) -> NotificationPreferencesRepository:
        from app.context.notification.infrastructure.persistence.mappers.notification_preferences_mapper import (
            NotificationPreferencesMapper,
        )
        return SqlNotificationPreferencesRepository(
            session=session,
            mapper=NotificationPreferencesMapper(),
        )

    async def _load_aggregate(self, user_id: str) -> NotificationPreferences | None:
        if self._session_factory is not None:
            async with self._session_factory() as session:
                repo = self._make_repo(session)
                return await repo.get_by_user_id(Id.from_string(user_id))
        return await self._repo.get_by_user_id(Id.from_string(user_id))

    async def get_reminder_window(self, user_id: str) -> int:
        aggregate = await self._load_aggregate(user_id)
        if aggregate is None:
            return 24

        return aggregate.reminder_window_hours
