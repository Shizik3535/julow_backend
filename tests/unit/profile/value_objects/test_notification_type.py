"""Unit-тесты для NotificationType."""

import pytest

from app.context.profile.domain.value_objects.notification_type import NotificationType


@pytest.mark.unit
class TestNotificationType:
    def test_all_types_exist(self) -> None:
        assert NotificationType.TASK_ASSIGNED.value == "task_assigned"
        assert NotificationType.TASK_UPDATED.value == "task_updated"
        assert NotificationType.MENTION.value == "mention"
        assert NotificationType.COMMENT_ADDED.value == "comment_added"
        assert NotificationType.MEETING_REMINDER.value == "meeting_reminder"
        assert NotificationType.SYSTEM_ANNOUNCEMENT.value == "system_announcement"
        assert NotificationType.DEADLINE_APPROACHING.value == "deadline_approaching"

    def test_types_are_distinct(self) -> None:
        values = [t.value for t in NotificationType]
        assert len(values) == len(set(values))
