"""Unit-тесты для NotificationChannel."""

import pytest

from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


@pytest.mark.unit
class TestNotificationChannel:
    def test_all_channels_exist(self) -> None:
        assert NotificationChannel.IN_APP.value == "in_app"
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.PUSH.value == "push"
        assert NotificationChannel.SMS.value == "sms"

    def test_channels_are_distinct(self) -> None:
        values = [c.value for c in NotificationChannel]
        assert len(values) == len(set(values))
