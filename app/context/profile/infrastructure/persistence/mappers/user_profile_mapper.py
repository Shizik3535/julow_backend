from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.language_code_vo import LanguageCode
from app.shared.domain.value_objects.timezone_vo import Timezone
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.entities.pinned_item import PinnedItem
from app.context.profile.domain.entities.social_link import SocialLink
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.custom_theme import CustomTheme
from app.context.profile.domain.value_objects.date_format import DateFormat
from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction
from app.context.profile.domain.value_objects.hotkey_config import HotkeyConfig
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility
from app.context.profile.domain.value_objects.sidebar_section import SidebarSection
from app.context.profile.domain.value_objects.start_page import StartPage
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.time_format import TimeFormat
from app.context.profile.domain.value_objects.week_start_day import WeekStartDay

from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import (
    HotkeyConfigORM,
    PinnedItemORM,
    SidebarSectionORM,
    SocialLinkORM,
    UserProfileORM,
)


class UserProfileMapper(BaseMapper[UserProfile, UserProfileORM]):
    """Data Mapper: UserProfile ↔ UserProfileORM + все дочерние ORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: UserProfileORM) -> UserProfile:
        custom_theme = None
        if orm_model.custom_theme_name is not None:
            colors = {
                k: Color(v) for k, v in (orm_model.custom_theme_colors or {}).items()
            }
            custom_theme = CustomTheme(name=orm_model.custom_theme_name, colors=colors)

        appearance = AppearanceSettings(
            theme=Theme(orm_model.theme),
            accent_color=Color(orm_model.accent_color),
            custom_theme=custom_theme,
            interface_density=InterfaceDensity(orm_model.interface_density),
        )

        localization = LocalizationSettings(
            language=LanguageCode(orm_model.language),
            timezone=Timezone(orm_model.timezone_),
            date_format=DateFormat(orm_model.date_format),
            time_format=TimeFormat(orm_model.time_format),
            week_start_day=WeekStartDay(orm_model.week_start_day),
        )

        navigation = NavigationSettings(
            start_page=StartPage(orm_model.start_page),
        )

        privacy = PrivacySettings(
            profile_visibility=ProfileVisibility(orm_model.profile_visibility),
            online_status_visibility=OnlineStatusVisibility(orm_model.online_status_visibility),
            activity_tracking_consent=ActivityTrackingConsent(orm_model.activity_tracking_consent),
        )

        social_links = [
            SocialLink(
                id=self._map_id(sl.id),
                platform=sl.platform,
                url=Url(sl.url),
                display_name=sl.display_name,
            )
            for sl in orm_model.social_links
        ]

        pinned_items = [
            PinnedItem(
                id=self._map_id(pi.id),
                target_type=PinnedTargetType(pi.target_type),
                target_id=self._map_id(pi.target_id),
                order=pi.order,
                pinned_at=pi.pinned_at,
            )
            for pi in orm_model.pinned_items
        ]

        hotkeys = [
            HotkeyConfig(
                action=HotkeyAction(hk.action),
                key_combination=hk.key_combination,
                is_enabled=hk.is_enabled,
            )
            for hk in orm_model.hotkeys
        ]

        sidebar_sections = [
            SidebarSection(
                section_id=ss.section_id,
                is_collapsed=ss.is_collapsed,
                item_ids=[Id.from_string(iid) for iid in (ss.item_ids or [])],
                order=ss.order,
            )
            for ss in orm_model.sidebar_sections
        ]

        return UserProfile(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            display_name=orm_model.display_name,
            avatar_url=Url(orm_model.avatar_url) if orm_model.avatar_url else None,
            bio=orm_model.bio,
            job_title=orm_model.job_title,
            social_links=social_links,
            appearance=appearance,
            localization=localization,
            navigation=navigation,
            privacy=privacy,
            hotkeys=hotkeys,
            sidebar_sections=sidebar_sections,
            pinned_items=pinned_items,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: UserProfile) -> UserProfileORM:
        custom_theme_name = None
        custom_theme_colors = None
        if aggregate.appearance.custom_theme is not None:
            custom_theme_name = aggregate.appearance.custom_theme.name
            custom_theme_colors = {
                k: str(v) for k, v in aggregate.appearance.custom_theme.colors.items()
            }

        orm = UserProfileORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            display_name=aggregate.display_name,
            avatar_url=str(aggregate.avatar_url) if aggregate.avatar_url else None,
            bio=aggregate.bio,
            job_title=aggregate.job_title,
            # Appearance
            theme=aggregate.appearance.theme.value,
            accent_color=str(aggregate.appearance.accent_color),
            custom_theme_name=custom_theme_name,
            custom_theme_colors=custom_theme_colors,
            interface_density=aggregate.appearance.interface_density.value,
            # Localization
            language=str(aggregate.localization.language),
            timezone_=str(aggregate.localization.timezone),
            date_format=str(aggregate.localization.date_format),
            time_format=aggregate.localization.time_format.value,
            week_start_day=aggregate.localization.week_start_day.value,
            # Navigation
            start_page=str(aggregate.navigation.start_page),
            # Privacy
            profile_visibility=aggregate.privacy.profile_visibility.value,
            online_status_visibility=aggregate.privacy.online_status_visibility.value,
            activity_tracking_consent=aggregate.privacy.activity_tracking_consent.value,
            # Timestamps
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        # Children
        orm.social_links = [self._social_link_to_orm(sl, aggregate.id) for sl in aggregate.social_links]
        orm.pinned_items = [self._pinned_item_to_orm(pi, aggregate.id) for pi in aggregate.pinned_items]
        orm.hotkeys = [self._hotkey_to_orm(hk, aggregate.id) for hk in aggregate.hotkeys]
        orm.sidebar_sections = [self._sidebar_to_orm(ss, aggregate.id) for ss in aggregate.sidebar_sections]

        return orm

    # ------------------------------------------------------------------
    # Child mappers: Domain → ORM
    # ------------------------------------------------------------------

    def _social_link_to_orm(self, sl: SocialLink, profile_id: Id) -> SocialLinkORM:
        return SocialLinkORM(
            id=self._map_uuid(sl.id),
            profile_id=self._map_uuid(profile_id),
            platform=sl.platform,
            url=str(sl.url),
            display_name=sl.display_name,
        )

    def _pinned_item_to_orm(self, pi: PinnedItem, profile_id: Id) -> PinnedItemORM:
        return PinnedItemORM(
            id=self._map_uuid(pi.id),
            profile_id=self._map_uuid(profile_id),
            target_type=pi.target_type.value,
            target_id=self._map_uuid(pi.target_id),
            order=pi.order,
            pinned_at=pi.pinned_at,
        )

    def _hotkey_to_orm(self, hk: HotkeyConfig, profile_id: Id) -> HotkeyConfigORM:
        return HotkeyConfigORM(
            id=self._map_uuid(Id.generate()),
            profile_id=self._map_uuid(profile_id),
            action=hk.action.value,
            key_combination=hk.key_combination,
            is_enabled=hk.is_enabled,
        )

    def _sidebar_to_orm(self, ss: SidebarSection, profile_id: Id) -> SidebarSectionORM:
        return SidebarSectionORM(
            id=self._map_uuid(Id.generate()),
            profile_id=self._map_uuid(profile_id),
            section_id=ss.section_id,
            is_collapsed=ss.is_collapsed,
            item_ids=[str(iid) for iid in ss.item_ids],
            order=ss.order,
        )
