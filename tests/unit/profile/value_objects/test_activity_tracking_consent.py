"""Unit-тесты для ActivityTrackingConsent."""

import pytest

from app.context.profile.domain.value_objects.activity_tracking_consent import ActivityTrackingConsent


@pytest.mark.unit
class TestActivityTrackingConsent:
    def test_all_consents_exist(self) -> None:
        assert ActivityTrackingConsent.GRANTED.value == "granted"
        assert ActivityTrackingConsent.DENIED.value == "denied"

    def test_consents_are_distinct(self) -> None:
        values = [c.value for c in ActivityTrackingConsent]
        assert len(values) == len(set(values))
