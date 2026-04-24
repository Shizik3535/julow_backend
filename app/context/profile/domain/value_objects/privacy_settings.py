from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility
from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility
from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent


@dataclass(frozen=True)
class PrivacySettings(ValueObject):
    """
    Группа настроек приватности.

    Атрибуты:
        profile_visibility: Видимость профиля.
        online_status_visibility: Видимость онлайн-статуса.
        activity_tracking_consent: Согласие на отслеживание активности.
    """

    profile_visibility: ProfileVisibility = ProfileVisibility.ORGANIZATION_ONLY
    online_status_visibility: OnlineStatusVisibility = OnlineStatusVisibility.EVERYONE
    activity_tracking_consent: ActivityTrackingConsent = ActivityTrackingConsent.GRANTED
