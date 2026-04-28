from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.infrastructure.persistence.mappers.notification_preferences_mapper import (
    NotificationPreferencesMapper,
)
from app.context.notification.infrastructure.persistence.orm_models.notification_preferences_orm import (
    NotificationPreferencesORM,
    PreferenceEntryORM,
)


class SqlNotificationPreferencesRepository(
    SqlAlchemyRepository[NotificationPreferences, NotificationPreferencesORM],
    NotificationPreferencesRepository,
):
    """SQLAlchemy-реализация NotificationPreferencesRepository."""

    def __init__(self, session: AsyncSession, mapper: NotificationPreferencesMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=NotificationPreferencesORM)

    async def get_by_user_id(self, user_id: Id) -> NotificationPreferences | None:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(NotificationPreferencesORM).where(NotificationPreferencesORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def update(self, aggregate: NotificationPreferences) -> NotificationPreferences:
        """Обновляет агрегат с полной синхронизацией дочерних preference_entries."""
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(NotificationPreferencesORM).where(NotificationPreferencesORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="NotificationPreferences", id=aggregate.id)

        # Обновить скалярные поля
        updated_orm = self._mapper.to_orm(aggregate)
        for column in NotificationPreferencesORM.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        # Синхронизация дочерних: delete old + insert new
        await self._session.execute(
            PreferenceEntryORM.__table__.delete().where(
                PreferenceEntryORM.preferences_id == uuid_val
            )
        )
        for entry_orm in updated_orm.preference_entries:
            entry_orm.preferences_id = uuid_val
            self._session.add(entry_orm)

        await self._session.flush()
        return aggregate
