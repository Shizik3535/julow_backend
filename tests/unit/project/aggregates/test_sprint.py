"""Unit-тесты для агрегата Sprint (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.date_range_vo import DateRange
from tests.factories import IdFactory
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.events.sprint_events import (
    SprintCreated,
    SprintStarted,
    SprintCompleted,
    SprintCancelled,
    SprintGoalUpdated,
    SprintRetroCreated,
    TasksMovedToNextSprint,
    TasksMovedToBacklog,
)
from app.context.project.domain.exceptions.sprint_exceptions import (
    SprintAlreadyStartedException,
    SprintNotStartedException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintCreation:
    def test_create_with_defaults(self, new_sprint: Sprint) -> None:
        assert new_sprint.name == "Sprint 1"
        assert new_sprint.status == SprintStatus.PLANNING
        assert new_sprint.project_id is not None
        assert new_sprint.goal is None
        assert new_sprint.date_range is None

    def test_create_emits_event(self, new_sprint: Sprint) -> None:
        events = new_sprint.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], SprintCreated)

    def test_create_with_goal(self) -> None:
        goal = SprintGoal(value="Deliver auth")
        sprint = Sprint.create(name="Sprint 1", project_id=IdFactory(), goal=goal)
        assert sprint.goal is not None
        assert sprint.goal.value == "Deliver auth"


# ═══════════════════════════════════════════════════════════════════════════
# Запуск
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintStart:
    def test_start(self, sprint: Sprint) -> None:
        sprint.start()
        assert sprint.status == SprintStatus.ACTIVE

    def test_start_emits_event(self, sprint: Sprint) -> None:
        sprint.start()
        events = sprint.clear_domain_events()
        assert any(isinstance(e, SprintStarted) for e in events)

    def test_start_already_started_raises(self, active_sprint: Sprint) -> None:
        with pytest.raises(SprintAlreadyStartedException):
            active_sprint.start()

    def test_start_from_completed_raises(self, active_sprint: Sprint) -> None:
        active_sprint.complete()
        active_sprint.clear_domain_events()
        with pytest.raises(SprintAlreadyStartedException):
            active_sprint.start()


# ═══════════════════════════════════════════════════════════════════════════
# Завершение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintComplete:
    def test_complete(self, active_sprint: Sprint) -> None:
        active_sprint.complete()
        assert active_sprint.status == SprintStatus.COMPLETED

    def test_complete_emits_event(self, active_sprint: Sprint) -> None:
        active_sprint.complete()
        events = active_sprint.clear_domain_events()
        assert any(isinstance(e, SprintCompleted) for e in events)

    def test_complete_not_started_raises(self, sprint: Sprint) -> None:
        with pytest.raises(SprintNotStartedException):
            sprint.complete()

    def test_complete_with_incomplete_tasks_to_next_sprint(self, active_sprint: Sprint) -> None:
        task_ids = [Id.generate(), Id.generate()]
        next_sprint_id = Id.generate()
        active_sprint.complete(incomplete_task_ids=task_ids, next_sprint_id=next_sprint_id)
        events = active_sprint.clear_domain_events()
        assert any(isinstance(e, SprintCompleted) for e in events)
        assert any(isinstance(e, TasksMovedToNextSprint) for e in events)

    def test_complete_with_incomplete_tasks_to_backlog(self, active_sprint: Sprint) -> None:
        task_ids = [Id.generate()]
        active_sprint.complete(incomplete_task_ids=task_ids)
        events = active_sprint.clear_domain_events()
        assert any(isinstance(e, SprintCompleted) for e in events)
        assert any(isinstance(e, TasksMovedToBacklog) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Отмена
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintCancel:
    def test_cancel_from_planning(self, sprint: Sprint) -> None:
        sprint.cancel()
        assert sprint.status == SprintStatus.CANCELLED

    def test_cancel_emits_event(self, sprint: Sprint) -> None:
        sprint.cancel()
        events = sprint.clear_domain_events()
        assert any(isinstance(e, SprintCancelled) for e in events)

    def test_cancel_from_active(self, active_sprint: Sprint) -> None:
        active_sprint.cancel()
        assert active_sprint.status == SprintStatus.CANCELLED

    def test_cancel_from_completed_is_noop(self, active_sprint: Sprint) -> None:
        active_sprint.complete()
        active_sprint.clear_domain_events()
        active_sprint.cancel()
        events = active_sprint.clear_domain_events()
        assert not any(isinstance(e, SprintCancelled) for e in events)

    def test_cancel_from_cancelled_is_noop(self, sprint: Sprint) -> None:
        sprint.cancel()
        sprint.clear_domain_events()
        sprint.cancel()
        events = sprint.clear_domain_events()
        assert not any(isinstance(e, SprintCancelled) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Цель
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintGoal:
    def test_update_goal(self, sprint: Sprint) -> None:
        goal = SprintGoal(value="New goal")
        sprint.update_goal(goal)
        assert sprint.goal == goal

    def test_update_goal_emits_event(self, sprint: Sprint) -> None:
        sprint.update_goal(SprintGoal(value="New goal"))
        events = sprint.clear_domain_events()
        assert any(isinstance(e, SprintGoalUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Диапазон дат
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintDateRange:
    def test_update_date_range(self, sprint: Sprint) -> None:
        from datetime import date
        date_range = DateRange(start=date(2025, 1, 1), end=date(2025, 1, 14))
        sprint.update_date_range(date_range)
        assert sprint.date_range == date_range

    def test_update_date_range_to_none(self, sprint: Sprint) -> None:
        sprint.update_date_range(None)
        assert sprint.date_range is None


# ═══════════════════════════════════════════════════════════════════════════
# Ретроспектива
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprintRetro:
    def test_create_retro(self, sprint: Sprint) -> None:
        sections = [RetroSection(title="What went well")]
        sprint.create_retro(template_name="Classic", sections=sections)
        assert sprint.retro is not None
        assert sprint.retro.template_name == "Classic"

    def test_create_retro_emits_event(self, sprint: Sprint) -> None:
        sprint.create_retro(template_name="Classic", sections=[])
        events = sprint.clear_domain_events()
        assert any(isinstance(e, SprintRetroCreated) for e in events)
