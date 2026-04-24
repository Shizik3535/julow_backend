"""Unit-тесты для ChannelPreference."""

import pytest

from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


@pytest.mark.unit
class TestChannelPreference:
    def test_enabled_channel(self) -> None:
        cp = ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=True)
        assert cp.channel == NotificationChannel.EMAIL
        assert cp.is_enabled is True

    def test_disabled_channel(self) -> None:
        cp = ChannelPreference(channel=NotificationChannel.SMS, is_enabled=False)
        assert not cp.is_enabled

    def test_frozen(self) -> None:
        cp = ChannelPreference(channel=NotificationChannel.IN_APP)
        with pytest.raises(Exception):
            cp.is_enabled = False

    def test_equality_by_value(self) -> None:
        cp1 = ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=True)
        cp2 = ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=True)
        assert cp1 == cp2
