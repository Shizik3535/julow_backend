"""
Profile BC conftest — фикстуры для unit-тестов Profile BC.

Содержит фабричные фикстуры для агрегатов и VOs,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.domain.value_objects.appearance_settings import AppearanceSettings
from app.context.profile.domain.value_objects.localization_settings import LocalizationSettings
from app.context.profile.domain.value_objects.navigation_settings import NavigationSettings
from app.context.profile.domain.value_objects.notification_settings import NotificationSettings
from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType
from tests.factories import IdFactory


# ── Агрегат UserProfile ──────────────────────────────────────────────────


@pytest.fixture
def new_profile() -> UserProfile:
    """Новый профиль со всеми настройками по умолчанию."""
    user_id = IdFactory()
    return UserProfile.create(user_id)


@pytest.fixture
def profile(new_profile: UserProfile) -> UserProfile:
    """Профиль с очищенными событиями (после создания)."""
    new_profile.clear_domain_events()
    return new_profile


# ── URL фикстуры ──────────────────────────────────────────────────────────


@pytest.fixture
def any_avatar_url() -> Url:
    """URL аватара по умолчанию."""
    return Url("https://cdn.example.com/avatar.png")


@pytest.fixture
def any_social_url() -> Url:
    """URL социальной ссылки."""
    return Url("https://github.com/user")
