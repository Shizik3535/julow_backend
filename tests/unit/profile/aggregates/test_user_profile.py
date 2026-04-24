"""Unit-тесты для агрегата UserProfile (Profile BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.events.profile_events import (
    AppearanceSettingsChanged,
    AvatarChanged,
    HotkeysChanged,
    LocalizationSettingsChanged,
    NavigationSettingsChanged,
    NotificationSettingsChanged,
    PersonalInfoChanged,
    PinnedItemAdded,
    PinnedItemRemoved,
    PrivacySettingsChanged,
    ProfileCreated,
    ProfileDeleted,
    SidebarConfigUpdated,
)
from app.context.profile.domain.exceptions.profile_exceptions import (
    DuplicatePinnedItemException,
    DuplicateSocialLinkException,
)
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.notification_settings import NotificationSettings
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType
from app.context.profile.domain.value_objects.hotkey_config import HotkeyConfig
from app.context.profile.domain.value_objects.hotkey_action import HotkeyAction
from app.context.profile.domain.value_objects.sidebar_section import SidebarSection
from app.context.profile.domain.value_objects.start_page import StartPage
from app.context.profile.domain.value_objects.date_format import DateFormat
from app.context.profile.domain.value_objects.time_format import TimeFormat
from app.context.profile.domain.value_objects.week_start_day import WeekStartDay
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility


# ═══════════════════════════════════════════════════════════════════════════
# Создание профиля
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileCreation:
    def test_create_with_defaults(self, new_profile: UserProfile) -> None:
        profile = new_profile
        assert profile.appearance.theme == Theme.SYSTEM
        assert profile.appearance.interface_density == InterfaceDensity.COMFORTABLE
        assert profile.localization.date_format == DateFormat("YYYY-MM-DD")
        assert profile.localization.time_format == TimeFormat.H24
        assert profile.localization.week_start_day == WeekStartDay.MONDAY
        assert profile.navigation.start_page == StartPage("dashboard")
        assert profile.privacy.profile_visibility == ProfileVisibility.ORGANIZATION_ONLY
        assert profile.avatar_url is None
        assert profile.bio is None
        assert profile.job_title is None
        assert profile.social_links == []
        assert profile.pinned_items == []
        assert profile.hotkeys == []

    def test_create_emits_event(self, new_profile: UserProfile) -> None:
        events = new_profile.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProfileCreated)
        assert events[0].user_id == str(new_profile.user_id)

    def test_create_sets_user_id(self) -> None:
        user_id = Id.generate()
        profile = UserProfile.create(user_id)
        assert profile.user_id == user_id


# ═══════════════════════════════════════════════════════════════════════════
# Аватар
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileAvatar:
    def test_change_avatar(self, profile: UserProfile, any_avatar_url: Url) -> None:
        profile.change_avatar(any_avatar_url)
        assert profile.avatar_url == any_avatar_url

    def test_change_avatar_emits_event(self, profile: UserProfile, any_avatar_url: Url) -> None:
        profile.change_avatar(any_avatar_url)
        events = profile.clear_domain_events()
        assert any(isinstance(e, AvatarChanged) for e in events)

    def test_change_avatar_updates_timestamp(self, profile: UserProfile, any_avatar_url: Url) -> None:
        before = profile.updated_at
        profile.change_avatar(any_avatar_url)
        assert profile.updated_at >= before


# ═══════════════════════════════════════════════════════════════════════════
# Персональные данные
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfilePersonalInfo:
    def test_update_bio(self, profile: UserProfile) -> None:
        profile.update_personal_info(bio="Hello world")
        assert profile.bio == "Hello world"

    def test_update_job_title(self, profile: UserProfile) -> None:
        profile.update_personal_info(job_title="Developer")
        assert profile.job_title == "Developer"

    def test_update_both(self, profile: UserProfile) -> None:
        profile.update_personal_info(bio="Bio", job_title="Dev")
        assert profile.bio == "Bio"
        assert profile.job_title == "Dev"

    def test_update_bio_emits_event(self, profile: UserProfile) -> None:
        profile.update_personal_info(bio="New bio")
        events = profile.clear_domain_events()
        assert any(isinstance(e, PersonalInfoChanged) for e in events)
        event = next(e for e in events if isinstance(e, PersonalInfoChanged))
        assert "bio" in event.changed_fields

    def test_update_job_title_emits_event(self, profile: UserProfile) -> None:
        profile.update_personal_info(job_title="Lead")
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, PersonalInfoChanged))
        assert "job_title" in event.changed_fields

    def test_no_change_no_event(self, profile: UserProfile) -> None:
        profile.update_personal_info(bio=None, job_title=None)
        events = profile.clear_domain_events()
        assert not any(isinstance(e, PersonalInfoChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Социальные ссылки
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileSocialLinks:
    def test_add_social_link(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url)
        assert len(profile.social_links) == 1
        assert profile.social_links[0].platform == "github"

    def test_add_social_link_with_display_name(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url, display_name="My GitHub")
        assert profile.social_links[0].display_name == "My GitHub"

    def test_add_social_link_emits_event(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url)
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, PersonalInfoChanged))
        assert "social_links" in event.changed_fields

    def test_duplicate_social_link_raises(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url)
        with pytest.raises(DuplicateSocialLinkException):
            profile.add_social_link("github", Url("https://github.com/other"))

    def test_remove_social_link(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url)
        profile.clear_domain_events()
        profile.remove_social_link("github")
        assert len(profile.social_links) == 0

    def test_remove_social_link_emits_event(self, profile: UserProfile, any_social_url: Url) -> None:
        profile.add_social_link("github", any_social_url)
        profile.clear_domain_events()
        profile.remove_social_link("github")
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, PersonalInfoChanged))
        assert "social_links" in event.changed_fields


# ═══════════════════════════════════════════════════════════════════════════
# Настройки внешнего вида
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileAppearance:
    def test_update_appearance(self, profile: UserProfile) -> None:
        new_settings = AppearanceSettings(theme=Theme.DARK)
        profile.update_appearance(new_settings)
        assert profile.appearance.theme == Theme.DARK

    def test_update_appearance_emits_event(self, profile: UserProfile) -> None:
        new_settings = AppearanceSettings(theme=Theme.DARK)
        profile.update_appearance(new_settings)
        events = profile.clear_domain_events()
        assert any(isinstance(e, AppearanceSettingsChanged) for e in events)

    def test_update_appearance_tracks_changed_fields(self, profile: UserProfile) -> None:
        new_settings = AppearanceSettings(theme=Theme.DARK)
        profile.update_appearance(new_settings)
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, AppearanceSettingsChanged))
        assert "theme" in event.changed_fields

    def test_update_appearance_no_change_no_event(self, profile: UserProfile) -> None:
        profile.update_appearance(profile.appearance)
        events = profile.clear_domain_events()
        assert not any(isinstance(e, AppearanceSettingsChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Настройки локализации
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileLocalization:
    def test_update_localization(self, profile: UserProfile) -> None:
        new_settings = LocalizationSettings(date_format=DateFormat("DD.MM.YYYY"))
        profile.update_localization(new_settings)
        assert profile.localization.date_format == DateFormat("DD.MM.YYYY")

    def test_update_localization_emits_event(self, profile: UserProfile) -> None:
        new_settings = LocalizationSettings(date_format=DateFormat("DD.MM.YYYY"))
        profile.update_localization(new_settings)
        events = profile.clear_domain_events()
        assert any(isinstance(e, LocalizationSettingsChanged) for e in events)

    def test_update_localization_tracks_changed_fields(self, profile: UserProfile) -> None:
        new_settings = LocalizationSettings(date_format=DateFormat("DD.MM.YYYY"))
        profile.update_localization(new_settings)
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, LocalizationSettingsChanged))
        assert "date_format" in event.changed_fields

    def test_update_localization_no_change_no_event(self, profile: UserProfile) -> None:
        profile.update_localization(profile.localization)
        events = profile.clear_domain_events()
        assert not any(isinstance(e, LocalizationSettingsChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Настройки навигации
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileNavigation:
    def test_update_navigation(self, profile: UserProfile) -> None:
        new_settings = NavigationSettings(start_page=StartPage("my_tasks"))
        profile.update_navigation(new_settings)
        assert profile.navigation.start_page == StartPage("my_tasks")

    def test_update_navigation_emits_event(self, profile: UserProfile) -> None:
        new_settings = NavigationSettings(start_page=StartPage("inbox"))
        profile.update_navigation(new_settings)
        events = profile.clear_domain_events()
        assert any(isinstance(e, NavigationSettingsChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Настройки уведомлений
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileNotifications:
    def test_update_notifications(self, profile: UserProfile) -> None:
        new_settings = NotificationSettings()
        profile.update_notifications(new_settings)
        assert profile.notifications == new_settings

    def test_update_notifications_emits_event(self, profile: UserProfile) -> None:
        new_settings = NotificationSettings()
        profile.update_notifications(new_settings)
        events = profile.clear_domain_events()
        # Default settings equal, so no event
        assert not any(isinstance(e, NotificationSettingsChanged) for e in events)

    def test_update_notifications_with_change_emits_event(self, profile: UserProfile) -> None:
        from app.context.profile.domain.value_objects.type_preference import TypePreference
        from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
        from app.context.profile.domain.value_objects.notification_type import NotificationType
        from app.context.profile.domain.value_objects.notification_channel import NotificationChannel
        new_settings = NotificationSettings(
            type_preferences=[
                TypePreference(
                    notification_type=NotificationType.TASK_ASSIGNED,
                    channels=[
                        ChannelPreference(channel=NotificationChannel.IN_APP, is_enabled=False),
                        ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=True),
                    ],
                    is_enabled=False,
                ),
            ]
        )
        profile.update_notifications(new_settings)
        events = profile.clear_domain_events()
        assert any(isinstance(e, NotificationSettingsChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Настройки приватности
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfilePrivacy:
    def test_update_privacy(self, profile: UserProfile) -> None:
        new_settings = PrivacySettings(profile_visibility=ProfileVisibility.PRIVATE)
        profile.update_privacy(new_settings)
        assert profile.privacy.profile_visibility == ProfileVisibility.PRIVATE

    def test_update_privacy_emits_event(self, profile: UserProfile) -> None:
        new_settings = PrivacySettings(profile_visibility=ProfileVisibility.PRIVATE)
        profile.update_privacy(new_settings)
        events = profile.clear_domain_events()
        assert any(isinstance(e, PrivacySettingsChanged) for e in events)

    def test_update_privacy_tracks_changed_fields(self, profile: UserProfile) -> None:
        new_settings = PrivacySettings(profile_visibility=ProfileVisibility.PRIVATE)
        profile.update_privacy(new_settings)
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, PrivacySettingsChanged))
        assert "profile_visibility" in event.changed_fields


# ═══════════════════════════════════════════════════════════════════════════
# Горячие клавиши
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileHotkeys:
    def test_update_hotkeys(self, profile: UserProfile) -> None:
        configs = [HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K")]
        profile.update_hotkeys(configs)
        assert len(profile.hotkeys) == 1
        assert profile.hotkeys[0].action == HotkeyAction.SEARCH

    def test_update_hotkeys_emits_event(self, profile: UserProfile) -> None:
        configs = [HotkeyConfig(action=HotkeyAction.SEARCH, key_combination="Ctrl+K")]
        profile.update_hotkeys(configs)
        events = profile.clear_domain_events()
        assert any(isinstance(e, HotkeysChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileSidebar:
    def test_update_sidebar(self, profile: UserProfile) -> None:
        sections = [SidebarSection(section_id="nav", order=0)]
        profile.update_sidebar(sections)
        assert len(profile.sidebar_sections) == 1

    def test_update_sidebar_emits_event(self, profile: UserProfile) -> None:
        sections = [SidebarSection(section_id="nav", order=0)]
        profile.update_sidebar(sections)
        events = profile.clear_domain_events()
        assert any(isinstance(e, SidebarConfigUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Закреплённые элементы
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfilePinnedItems:
    def test_pin_item(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.PROJECT, tid)
        assert len(profile.pinned_items) == 1
        assert profile.pinned_items[0].target_type == PinnedTargetType.PROJECT
        assert profile.pinned_items[0].target_id == tid

    def test_pin_item_emits_event(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, tid)
        events = profile.clear_domain_events()
        event = next(e for e in events if isinstance(e, PinnedItemAdded))
        assert event.target_type == PinnedTargetType.TASK
        assert event.target_id == str(tid)

    def test_pin_item_auto_order(self, profile: UserProfile) -> None:
        profile.pin_item(PinnedTargetType.PROJECT, Id.generate())
        profile.pin_item(PinnedTargetType.TASK, Id.generate())
        assert profile.pinned_items[0].order == 0
        assert profile.pinned_items[1].order == 1

    def test_duplicate_pin_raises(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, tid)
        with pytest.raises(DuplicatePinnedItemException):
            profile.pin_item(PinnedTargetType.TASK, tid)

    def test_same_id_different_type_allowed(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, tid)
        profile.pin_item(PinnedTargetType.PROJECT, tid)
        assert len(profile.pinned_items) == 2

    def test_unpin_item(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, tid)
        profile.clear_domain_events()
        profile.unpin_item(PinnedTargetType.TASK, tid)
        assert len(profile.pinned_items) == 0

    def test_unpin_item_emits_event(self, profile: UserProfile) -> None:
        tid = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, tid)
        profile.clear_domain_events()
        profile.unpin_item(PinnedTargetType.TASK, tid)
        events = profile.clear_domain_events()
        assert any(isinstance(e, PinnedItemRemoved) for e in events)

    def test_reorder_pinned_items(self, profile: UserProfile) -> None:
        id1 = Id.generate()
        id2 = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, id1)
        profile.pin_item(PinnedTargetType.PROJECT, id2)
        profile.clear_domain_events()
        # Reverse order
        profile.reorder_pinned_items([id2, id1])
        assert profile.pinned_items[0].target_id == id2
        assert profile.pinned_items[1].target_id == id1


# ═══════════════════════════════════════════════════════════════════════════
# Удаление профиля
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserProfileDeletion:
    def test_delete_emits_event(self, profile: UserProfile) -> None:
        profile.delete()
        events = profile.clear_domain_events()
        assert any(isinstance(e, ProfileDeleted) for e in events)
