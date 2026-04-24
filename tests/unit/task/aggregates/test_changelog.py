"""Unit-тесты для агрегата ChangelogEntry (Task BC)."""

import pytest

from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.events.changelog_events import ChangelogEntryCreated


@pytest.mark.unit
class TestChangelogEntryCreation:
    def test_create(self, new_changelog_entry: ChangelogEntry, any_project_id, any_reporter_id) -> None:
        assert new_changelog_entry.task_id == any_project_id
        assert new_changelog_entry.field_name == "status"
        assert new_changelog_entry.old_value == "open"
        assert new_changelog_entry.new_value == "closed"
        assert new_changelog_entry.changed_by == any_reporter_id
        assert new_changelog_entry.changed_at is not None

    def test_create_emits_event(self, new_changelog_entry: ChangelogEntry) -> None:
        events = new_changelog_entry.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ChangelogEntryCreated)
        assert events[0].field_name == "status"
