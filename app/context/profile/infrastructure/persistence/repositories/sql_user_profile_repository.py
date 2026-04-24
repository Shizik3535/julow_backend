from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.infrastructure.persistence.mappers.user_profile_mapper import UserProfileMapper
from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import (
    HotkeyConfigORM,
    NotificationPreferenceORM,
    PinnedItemORM,
    SidebarSectionORM,
    SocialLinkORM,
    UserProfileORM,
)


class SqlUserProfileRepository(SqlAlchemyRepository[UserProfile, UserProfileORM], UserProfileRepository):
    """SQLAlchemy-реализация UserProfileRepository."""

    def __init__(self, session: AsyncSession, mapper: UserProfileMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=UserProfileORM)

    async def get_by_user_id(self, user_id: Id) -> UserProfile | None:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(UserProfileORM).where(UserProfileORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[UserProfile]:
        stmt = select(UserProfileORM)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_role(self, role_id: Id) -> list[UserProfile]:
        # Делегируется на уровень application-слоя через IdentityUserPort.
        # Здесь возвращаем пустой список — вызывающий код должен
        # сначала получить user_ids из Identity BC, затем загрузить профили.
        return []

    async def add(self, aggregate: UserProfile) -> UserProfile:
        """Добавляет профиль со всеми дочерними сущностями."""
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)
        await self._session.flush()
        return aggregate

    async def update(self, aggregate: UserProfile) -> UserProfile:
        """Обновляет профиль с полной синхронизацией дочерних сущностей.

        Паттерн: обновить скалярные поля → удалить старые дочерние строки →
        вставить новые дочерние ORM-объекты.
        """
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(UserProfileORM).where(UserProfileORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
            raise EntityNotFoundException(entity_type="UserProfile", id=aggregate.id)

        # Обновить скалярные поля
        updated_orm = self._mapper.to_orm(aggregate)
        for column in UserProfileORM.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        # Синхронизация дочерних: delete old + insert new
        await self._session.execute(
            SocialLinkORM.__table__.delete().where(SocialLinkORM.profile_id == uuid_val)
        )
        await self._session.execute(
            PinnedItemORM.__table__.delete().where(PinnedItemORM.profile_id == uuid_val)
        )
        await self._session.execute(
            HotkeyConfigORM.__table__.delete().where(HotkeyConfigORM.profile_id == uuid_val)
        )
        await self._session.execute(
            SidebarSectionORM.__table__.delete().where(SidebarSectionORM.profile_id == uuid_val)
        )
        await self._session.execute(
            NotificationPreferenceORM.__table__.delete().where(NotificationPreferenceORM.profile_id == uuid_val)
        )

        for sl in updated_orm.social_links:
            sl.profile_id = uuid_val
            self._session.add(sl)
        for pi in updated_orm.pinned_items:
            pi.profile_id = uuid_val
            self._session.add(pi)
        for hk in updated_orm.hotkeys:
            hk.profile_id = uuid_val
            self._session.add(hk)
        for ss in updated_orm.sidebar_sections:
            ss.profile_id = uuid_val
            self._session.add(ss)
        for np in updated_orm.notification_preferences:
            np.profile_id = uuid_val
            self._session.add(np)

        await self._session.flush()
        return aggregate
