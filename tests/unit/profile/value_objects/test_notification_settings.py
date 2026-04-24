"""Unit-тесты для NotificationSettings."""

import pytest

from app.shared.domain.exceptions import BusinessRuleViolationException
from app.context.profile.domain.value_objects.notification_settings import NotificationSettings
from app.context.profile.domain.value_objects.type_preference import TypePreference
from app.context.profile.domain.value_objects.channel_preference import ChannelPreference
from app.context.profile.domain.value_objects.notification_type import NotificationType
from app.context.profile.domain.value_objects.notification_channel import NotificationChannel


@pytest.mark.unit
class TestNotificationSettings:
    def test_defaults_all_types_enabled(self) -> None:
        settings = NotificationSettings()
        assert len(settings.type_preferences) == len(NotificationType)
        for tp in settings.type_preferences:
            assert tp.is_enabled is True

    def test_defaults_in_app_and_email_enabled(self) -> None:
        settings = NotificationSettings()
        for tp in settings.type_preferences:
            in_app = next(c for c in tp.channels if c.channel == NotificationChannel.IN_APP)
            email = next(c for c in tp.channels if c.channel == NotificationChannel.EMAIL)
            assert in_app.is_enabled is True
            assert email.is_enabled is True

    def test_defaults_push_and_sms_disabled(self) -> None:
        settings = NotificationSettings()
        for tp in settings.type_preferences:
            push = next(c for c in tp.channels if c.channel == NotificationChannel.PUSH)
            sms = next(c for c in tp.channels if c.channel == NotificationChannel.SMS)
            assert push.is_enabled is False
            assert sms.is_enabled is False

    def test_enabled_type_without_enabled_channel_raises(self) -> None:
        with pytest.raises(BusinessRuleViolationException):
            NotificationSettings(
                type_preferences=[
                    TypePreference(
                        notification_type=NotificationType.TASK_ASSIGNED,
                        channels=[
                            ChannelPreference(channel=NotificationChannel.IN_APP, is_enabled=False),
                            ChannelPreference(channel=NotificationChannel.EMAIL, is_enabled=False),
                        ],
                        is_enabled=True,
                    ),
                ]
            )

    def test_disabled_type_without_channels_ok(self) -> None:
        settings = NotificationSettings(
            type_preferences=[
                TypePreference(
                    notification_type=NotificationType.TASK_ASSIGNED,
                    channels=[
                        ChannelPreference(channel=NotificationChannel.IN_APP, is_enabled=False),
                    ],
                    is_enabled=False,
                ),
            ]
        )
        assert len(settings.type_preferences) == 1

    def test_frozen(self) -> None:
        settings = NotificationSettings()
        with pytest.raises(Exception):
            settings.type_preferences = []

    def test_equality_by_value(self) -> None:
        s1 = NotificationSettings()
        s2 = NotificationSettings()
        assert s1 == s2
