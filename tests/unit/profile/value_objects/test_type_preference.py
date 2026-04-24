"""Unit-тесты для TypePreference."""

import pytest

from app.context.profile.domain.value_objects.type_preference import TypePreference
from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


@pytest.mark.unit
class TestTypePreference:
    def test_enabled_type_with_channels(self) -> None:
        tp = TypePreference(
            notification_type=NotificationType.TASK_ASSIGNED,
            channels=[
                ChannelPreference(channel=NotificationChannel.IN_APP, is_enabled=True),
            ],
            is_enabled=True,
        )
        assert tp.is_enabled is True
        assert len(tp.channels) == 1

    def test_disabled_type(self) -> None:
        tp = TypePreference(
            notification_type=NotificationType.MENTION,
            is_enabled=False,
        )
        assert not tp.is_enabled

    def test_frozen(self) -> None:
        tp = TypePreference(notification_type=NotificationType.TASK_ASSIGNED, is_enabled=True)
        with pytest.raises(Exception):
            tp.is_enabled = False

    def test_equality_by_value(self) -> None:
        tp1 = TypePreference(notification_type=NotificationType.TASK_ASSIGNED, is_enabled=True)
        tp2 = TypePreference(notification_type=NotificationType.TASK_ASSIGNED, is_enabled=True)
        assert tp1 == tp2
