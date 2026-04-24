"""Интеграционные тесты SqlUserProfileRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.entities.social_link import SocialLink
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)


@pytest.mark.integration
class TestSqlUserProfileRepositoryAdd:
    """Тесты добавления профиля."""

    async def test_add_and_get_by_id(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert found.id == profile.id
        assert found.user_id == profile.user_id

    async def test_add_persists_defaults(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert found.bio is None
        assert found.job_title is None
        assert found.avatar_url is None


@pytest.mark.integration
class TestSqlUserProfileRepositoryGetByUserId:
    """Тесты поиска по user_id."""

    async def test_get_by_user_id_found(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        found = await profile_repo.get_by_user_id(profile.user_id)
        assert found is not None
        assert found.id == profile.id

    async def test_get_by_user_id_not_found(self, profile_repo: SqlUserProfileRepository) -> None:
        found = await profile_repo.get_by_user_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlUserProfileRepositoryUpdate:
    """Тесты обновления профиля."""

    async def test_update_personal_info(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        profile.update_personal_info(bio="Hello world", job_title="Developer")
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert found.bio == "Hello world"
        assert found.job_title == "Developer"

    async def test_update_avatar(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        profile.change_avatar(Url("https://cdn.example.com/avatar.png"))
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert str(found.avatar_url) == "https://cdn.example.com/avatar.png"

    async def test_update_appearance(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        settings = AppearanceSettings(
            theme=Theme.DARK,
            interface_density=InterfaceDensity.COMPACT,
        )
        profile.update_appearance(settings)
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert found.appearance.theme == Theme.DARK
        assert found.appearance.interface_density == InterfaceDensity.COMPACT

    async def test_update_privacy(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        settings = PrivacySettings(
            profile_visibility=ProfileVisibility.PRIVATE,
            online_status_visibility=OnlineStatusVisibility.NOBODY,
            activity_tracking_consent=ActivityTrackingConsent.DENIED,
        )
        profile.update_privacy(settings)
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert found.privacy.profile_visibility == ProfileVisibility.PRIVATE
        assert found.privacy.online_status_visibility == OnlineStatusVisibility.NOBODY
        assert found.privacy.activity_tracking_consent == ActivityTrackingConsent.DENIED

    async def test_update_social_links_sync(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        profile.add_social_link(platform="github", url=Url("https://github.com/user"))
        profile.add_social_link(platform="linkedin", url=Url("https://linkedin.com/in/user"))
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert len(found.social_links) == 2

        # Удаляем одну ссылку
        found.remove_social_link("github")
        found.clear_domain_events()
        await profile_repo.update(found)

        reloaded = await profile_repo.get_by_id(profile.id)
        assert reloaded is not None
        assert len(reloaded.social_links) == 1
        assert reloaded.social_links[0].platform == "linkedin"

    async def test_update_pinned_items_sync(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        target1 = Id.generate()
        target2 = Id.generate()
        profile.pin_item(PinnedTargetType.TASK, target1)
        profile.pin_item(PinnedTargetType.PROJECT, target2)
        profile.clear_domain_events()
        await profile_repo.update(profile)

        found = await profile_repo.get_by_id(profile.id)
        assert found is not None
        assert len(found.pinned_items) == 2

        # Открепляем один элемент
        found.unpin_item(PinnedTargetType.TASK, target1)
        found.clear_domain_events()
        await profile_repo.update(found)

        reloaded = await profile_repo.get_by_id(profile.id)
        assert reloaded is not None
        assert len(reloaded.pinned_items) == 1
        assert reloaded.pinned_items[0].target_type == PinnedTargetType.PROJECT


@pytest.mark.integration
class TestSqlUserProfileRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        profile = await make_profile()
        await profile_repo.delete(profile.id)
        found = await profile_repo.get_by_id(profile.id)
        assert found is None


@pytest.mark.integration
class TestSqlUserProfileRepositorySearch:
    """Тесты поиска и пагинации."""

    async def test_get_all(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        await make_profile()
        await make_profile()
        profiles = await profile_repo.get_all(offset=0, limit=100)
        assert len(profiles) >= 2

    async def test_get_paginated(self, profile_repo: SqlUserProfileRepository, make_profile) -> None:
        await make_profile()
        await make_profile()
        await make_profile()
        profiles, total = await profile_repo.get_paginated(page=1, page_size=2)
        assert len(profiles) <= 2
        assert total >= 3
