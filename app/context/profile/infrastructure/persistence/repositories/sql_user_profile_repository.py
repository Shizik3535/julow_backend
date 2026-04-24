from __future__ import annotations

import uuid
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
        """Обновляет профиль с синхронизацией дочерних сущностей.

        Паттерн: обновить скалярные поля → diff-синхронизация дочерних
        через relationship-коллекции (update / delete-orphan / append).
        """
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(UserProfileORM).where(UserProfileORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
            raise EntityNotFoundException(entity_type="UserProfile", id=aggregate.id)

        # Обновить скалярные поля напрямую (без to_orm — избегаем identity conflict)
        custom_theme_name = None
        custom_theme_colors = None
        if aggregate.appearance.custom_theme is not None:
            custom_theme_name = aggregate.appearance.custom_theme.name
            custom_theme_colors = {
                k: str(v) for k, v in aggregate.appearance.custom_theme.colors.items()
            }

        orm_model.user_id = self._mapper._map_uuid(aggregate.user_id)
        orm_model.avatar_url = str(aggregate.avatar_url) if aggregate.avatar_url else None
        orm_model.bio = aggregate.bio
        orm_model.job_title = aggregate.job_title
        orm_model.theme = aggregate.appearance.theme.value
        orm_model.accent_color = str(aggregate.appearance.accent_color)
        orm_model.custom_theme_name = custom_theme_name
        orm_model.custom_theme_colors = custom_theme_colors
        orm_model.interface_density = aggregate.appearance.interface_density.value
        orm_model.language = str(aggregate.localization.language)
        orm_model.timezone_ = str(aggregate.localization.timezone)
        orm_model.date_format = str(aggregate.localization.date_format)
        orm_model.time_format = aggregate.localization.time_format.value
        orm_model.week_start_day = aggregate.localization.week_start_day.value
        orm_model.start_page = str(aggregate.navigation.start_page)
        orm_model.profile_visibility = aggregate.privacy.profile_visibility.value
        orm_model.online_status_visibility = aggregate.privacy.online_status_visibility.value
        orm_model.activity_tracking_consent = aggregate.privacy.activity_tracking_consent.value
        orm_model.updated_at = aggregate.updated_at

        # --- social_links (стабильный id) ---
        existing_sl: dict[uuid.UUID, SocialLinkORM] = {
            sl.id: sl for sl in list(orm_model.social_links)
        }
        desired_sl_ids = {self._mapper._map_uuid(sl.id) for sl in aggregate.social_links}
        for orm_sl in list(orm_model.social_links):
            if orm_sl.id not in desired_sl_ids:
                orm_model.social_links.remove(orm_sl)
        for sl in aggregate.social_links:
            sl_uuid = self._mapper._map_uuid(sl.id)
            if sl_uuid in existing_sl:
                orm_sl = existing_sl[sl_uuid]
                orm_sl.platform = sl.platform
                orm_sl.url = str(sl.url)
                orm_sl.display_name = sl.display_name
            else:
                orm_model.social_links.append(
                    self._mapper._social_link_to_orm(sl, aggregate.id)
                )

        # --- pinned_items (стабильный id) ---
        existing_pi: dict[uuid.UUID, PinnedItemORM] = {
            pi.id: pi for pi in list(orm_model.pinned_items)
        }
        desired_pi_ids = {self._mapper._map_uuid(pi.id) for pi in aggregate.pinned_items}
        for orm_pi in list(orm_model.pinned_items):
            if orm_pi.id not in desired_pi_ids:
                orm_model.pinned_items.remove(orm_pi)
        for pi in aggregate.pinned_items:
            pi_uuid = self._mapper._map_uuid(pi.id)
            if pi_uuid in existing_pi:
                orm_pi = existing_pi[pi_uuid]
                orm_pi.target_type = pi.target_type.value
                orm_pi.target_id = self._mapper._map_uuid(pi.target_id)
                orm_pi.order = pi.order
                orm_pi.pinned_at = pi.pinned_at
            else:
                orm_model.pinned_items.append(
                    self._mapper._pinned_item_to_orm(pi, aggregate.id)
                )

        # --- hotkeys (нет стабильного id → мэтч по action) ---
        existing_hk: dict[str, HotkeyConfigORM] = {
            hk.action: hk for hk in list(orm_model.hotkeys)
        }
        desired_actions = {hk.action.value for hk in aggregate.hotkeys}
        for orm_hk in list(orm_model.hotkeys):
            if orm_hk.action not in desired_actions:
                orm_model.hotkeys.remove(orm_hk)
        for hk in aggregate.hotkeys:
            action = hk.action.value
            if action in existing_hk:
                orm_hk = existing_hk[action]
                orm_hk.key_combination = hk.key_combination
                orm_hk.is_enabled = hk.is_enabled
            else:
                orm_model.hotkeys.append(
                    self._mapper._hotkey_to_orm(hk, aggregate.id)
                )

        # --- sidebar_sections (нет стабильного id → мэтч по section_id) ---
        existing_ss: dict[str, SidebarSectionORM] = {
            ss.section_id: ss for ss in list(orm_model.sidebar_sections)
        }
        desired_section_ids = {ss.section_id for ss in aggregate.sidebar_sections}
        for orm_ss in list(orm_model.sidebar_sections):
            if orm_ss.section_id not in desired_section_ids:
                orm_model.sidebar_sections.remove(orm_ss)
        for ss in aggregate.sidebar_sections:
            if ss.section_id in existing_ss:
                orm_ss = existing_ss[ss.section_id]
                orm_ss.is_collapsed = ss.is_collapsed
                orm_ss.item_ids = [str(iid) for iid in ss.item_ids]
                orm_ss.order = ss.order
            else:
                orm_model.sidebar_sections.append(
                    self._mapper._sidebar_to_orm(ss, aggregate.id)
                )

        # --- notification_preferences (нет стабильного id → мэтч по notification_type) ---
        existing_np: dict[str, NotificationPreferenceORM] = {
            np.notification_type: np for np in list(orm_model.notification_preferences)
        }
        desired_types = {
            tp.notification_type.value for tp in aggregate.notifications.type_preferences
        }
        for orm_np in list(orm_model.notification_preferences):
            if orm_np.notification_type not in desired_types:
                orm_model.notification_preferences.remove(orm_np)
        for tp in aggregate.notifications.type_preferences:
            ntype = tp.notification_type.value
            channels = {cp.channel.value: cp.is_enabled for cp in tp.channels}
            if ntype in existing_np:
                orm_np = existing_np[ntype]
                orm_np.is_enabled = tp.is_enabled
                orm_np.channels = channels
            else:
                orm_model.notification_preferences.append(
                    self._mapper._notification_domain_to_orm(tp, aggregate.id)
                )

        await self._session.flush()
        return aggregate
