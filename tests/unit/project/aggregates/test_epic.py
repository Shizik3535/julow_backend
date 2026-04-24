"""Unit-тесты для агрегата Epic (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.value_objects.epic_status import EpicStatus
from app.context.project.domain.events.epic_events import (
    EpicCreated,
    EpicUpdated,
    EpicStatusChanged,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEpicCreation:
    def test_create_with_defaults(self, new_epic: Epic) -> None:
        assert new_epic.name == "Test Epic"
        assert new_epic.status == EpicStatus.OPEN
        assert new_epic.project_id is not None
        assert new_epic.owner_id is not None

    def test_create_emits_event(self, new_epic: Epic) -> None:
        events = new_epic.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], EpicCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEpicUpdate:
    def test_update_name(self, epic: Epic) -> None:
        epic.update(name="New Name")
        assert epic.name == "New Name"

    def test_update_emits_event(self, epic: Epic) -> None:
        epic.update(name="New Name")
        events = epic.clear_domain_events()
        assert any(isinstance(e, EpicUpdated) for e in events)

    def test_update_tracks_changed_fields(self, epic: Epic) -> None:
        epic.update(name="New Name", color=Color("#FF5500"))
        events = epic.clear_domain_events()
        event = next(e for e in events if isinstance(e, EpicUpdated))
        assert "name" in event.changed_fields
        assert "color" in event.changed_fields

    def test_update_no_change_no_event(self, epic: Epic) -> None:
        epic.update(name=epic.name)
        events = epic.clear_domain_events()
        assert not any(isinstance(e, EpicUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEpicStatus:
    def test_change_status(self, epic: Epic) -> None:
        epic.change_status(EpicStatus.IN_PROGRESS)
        assert epic.status == EpicStatus.IN_PROGRESS

    def test_change_status_emits_event(self, epic: Epic) -> None:
        epic.change_status(EpicStatus.IN_PROGRESS)
        events = epic.clear_domain_events()
        assert any(isinstance(e, EpicStatusChanged) for e in events)
