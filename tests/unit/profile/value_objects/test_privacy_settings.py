"""Unit-тесты для PrivacySettings."""

import pytest

from app.context.profile.domain.value_objects.privacy_settings import PrivacySettings
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent


@pytest.mark.unit
class TestPrivacySettings:
    def test_defaults(self) -> None:
        settings = PrivacySettings()
        assert settings.profile_visibility == ProfileVisibility.ORGANIZATION_ONLY
        assert settings.online_status_visibility == OnlineStatusVisibility.EVERYONE
        assert settings.activity_tracking_consent == ActivityTrackingConsent.GRANTED

    def test_custom_settings(self) -> None:
        settings = PrivacySettings(
            profile_visibility=ProfileVisibility.PRIVATE,
            online_status_visibility=OnlineStatusVisibility.NOBODY,
            activity_tracking_consent=ActivityTrackingConsent.DENIED,
        )
        assert settings.profile_visibility == ProfileVisibility.PRIVATE
        assert settings.online_status_visibility == OnlineStatusVisibility.NOBODY

    def test_frozen(self) -> None:
        settings = PrivacySettings()
        with pytest.raises(Exception):
            settings.profile_visibility = ProfileVisibility.PUBLIC

    def test_equality_by_value(self) -> None:
        s1 = PrivacySettings()
        s2 = PrivacySettings()
        assert s1 == s2
