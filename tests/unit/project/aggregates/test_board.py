"""Unit-тесты для агрегата Board (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
from app.context.project.domain.value_objects.automation_action import AutomationAction
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.domain.value_objects.view_type import ViewType
from app.context.project.domain.events.board_events import (
    BoardColumnAdded,
    BoardColumnRemoved,
    BoardColumnReordered,
    WIPLimitChanged,
    SwimlaneAdded,
    SwimlaneRemoved,
    WorkflowStatusAdded,
    WorkflowStatusRemoved,
    WorkflowTransitionAdded,
    WorkflowTransitionRemoved,
    ProjectViewCreated,
    ProjectViewUpdated,
    ProjectViewDeleted,
    AutomationRuleCreated,
    AutomationRuleUpdated,
    AutomationRuleDeleted,
)
from app.context.project.domain.exceptions.board_exceptions import (
    BoardColumnNotFoundException,
    SwimlaneNotFoundException,
    WorkflowStatusNotFoundException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardCreation:
    def test_create_with_defaults(self, new_board: Board) -> None:
        assert new_board.project_id is not None
        assert len(new_board.columns) == 3
        assert len(new_board.workflow_statuses) == 3

    def test_create_sets_default_statuses(self, new_board: Board) -> None:
        names = [s.name for s in new_board.workflow_statuses]
        assert names == ["To Do", "In Progress", "Done"]
        categories = [s.category for s in new_board.workflow_statuses]
        assert categories == [
            WorkflowStatusCategory.TODO,
            WorkflowStatusCategory.IN_PROGRESS,
            WorkflowStatusCategory.DONE,
        ]


# ═══════════════════════════════════════════════════════════════════════════
# Колонки
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardColumns:
    def test_add_column(self, board: Board) -> None:
        board.add_column(name="Review")
        assert len(board.columns) == 4
        assert board.columns[3].name == "Review"

    def test_add_column_emits_event(self, board: Board) -> None:
        board.add_column(name="Review")
        events = board.clear_domain_events()
        assert any(isinstance(e, BoardColumnAdded) for e in events)

    def test_remove_column(self, board: Board) -> None:
        column_id = board.columns[0].id
        board.remove_column(column_id=column_id)
        assert len(board.columns) == 2

    def test_remove_column_emits_event(self, board: Board) -> None:
        column_id = board.columns[0].id
        board.remove_column(column_id=column_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, BoardColumnRemoved) for e in events)

    def test_remove_nonexistent_column_raises(self, board: Board) -> None:
        with pytest.raises(BoardColumnNotFoundException):
            board.remove_column(column_id=Id.generate())

    def test_reorder_columns(self, board: Board) -> None:
        col_ids = [board.columns[2].id, board.columns[0].id, board.columns[1].id]
        board.reorder_columns(column_ids=col_ids)
        assert board.columns[0].name == "Done"
        assert board.columns[1].name == "To Do"
        assert board.columns[2].name == "In Progress"

    def test_reorder_columns_emits_event(self, board: Board) -> None:
        col_ids = [c.id for c in board.columns]
        board.reorder_columns(column_ids=col_ids)
        events = board.clear_domain_events()
        assert any(isinstance(e, BoardColumnReordered) for e in events)

    def test_change_wip_limit(self, board: Board) -> None:
        column_id = board.columns[0].id
        wip = WIPLimit(value=5)
        board.change_wip_limit(column_id=column_id, wip_limit=wip)
        assert board.columns[0].wip_limit == wip

    def test_change_wip_limit_emits_event(self, board: Board) -> None:
        column_id = board.columns[0].id
        board.change_wip_limit(column_id=column_id, wip_limit=WIPLimit(value=5))
        events = board.clear_domain_events()
        assert any(isinstance(e, WIPLimitChanged) for e in events)

    def test_change_wip_limit_nonexistent_column_raises(self, board: Board) -> None:
        with pytest.raises(BoardColumnNotFoundException):
            board.change_wip_limit(column_id=Id.generate(), wip_limit=WIPLimit(value=5))


# ═══════════════════════════════════════════════════════════════════════════
# Swimlanes
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardSwimlanes:
    def test_add_swimlane(self, board: Board) -> None:
        board.add_swimlane(name="By Priority", group_by=SwimlaneGroupBy.PRIORITY)
        assert len(board.swimlanes) == 1

    def test_add_swimlane_emits_event(self, board: Board) -> None:
        board.add_swimlane(name="By Priority", group_by=SwimlaneGroupBy.PRIORITY)
        events = board.clear_domain_events()
        assert any(isinstance(e, SwimlaneAdded) for e in events)

    def test_remove_swimlane(self, board: Board) -> None:
        board.add_swimlane(name="By Priority", group_by=SwimlaneGroupBy.PRIORITY)
        swimlane_id = board.swimlanes[0].id
        board.remove_swimlane(swimlane_id=swimlane_id)
        assert len(board.swimlanes) == 0

    def test_remove_swimlane_emits_event(self, board: Board) -> None:
        board.add_swimlane(name="By Priority", group_by=SwimlaneGroupBy.PRIORITY)
        swimlane_id = board.swimlanes[0].id
        board.clear_domain_events()
        board.remove_swimlane(swimlane_id=swimlane_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, SwimlaneRemoved) for e in events)

    def test_remove_nonexistent_swimlane_raises(self, board: Board) -> None:
        with pytest.raises(SwimlaneNotFoundException):
            board.remove_swimlane(swimlane_id=Id.generate())


# ═══════════════════════════════════════════════════════════════════════════
# Workflow
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardWorkflow:
    def test_add_workflow_status(self, board: Board) -> None:
        board.add_workflow_status(name="In Review", category=WorkflowStatusCategory.REVIEW)
        assert len(board.workflow_statuses) == 4

    def test_add_workflow_status_emits_event(self, board: Board) -> None:
        board.add_workflow_status(name="In Review", category=WorkflowStatusCategory.REVIEW)
        events = board.clear_domain_events()
        assert any(isinstance(e, WorkflowStatusAdded) for e in events)

    def test_remove_workflow_status(self, board: Board) -> None:
        status_id = board.workflow_statuses[0].id
        board.remove_workflow_status(status_id=status_id)
        assert len(board.workflow_statuses) == 2

    def test_remove_workflow_status_emits_event(self, board: Board) -> None:
        status_id = board.workflow_statuses[0].id
        board.remove_workflow_status(status_id=status_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, WorkflowStatusRemoved) for e in events)

    def test_remove_nonexistent_workflow_status_raises(self, board: Board) -> None:
        with pytest.raises(WorkflowStatusNotFoundException):
            board.remove_workflow_status(status_id=Id.generate())

    def test_add_workflow_transition(self, board: Board) -> None:
        from_id = board.workflow_statuses[0].id
        to_id = board.workflow_statuses[1].id
        board.add_workflow_transition(from_status_id=from_id, to_status_id=to_id, name="Start")
        assert len(board.workflow_transitions) == 1

    def test_add_workflow_transition_emits_event(self, board: Board) -> None:
        from_id = board.workflow_statuses[0].id
        to_id = board.workflow_statuses[1].id
        board.add_workflow_transition(from_status_id=from_id, to_status_id=to_id, name="Start")
        events = board.clear_domain_events()
        assert any(isinstance(e, WorkflowTransitionAdded) for e in events)

    def test_remove_workflow_transition(self, board: Board) -> None:
        from_id = board.workflow_statuses[0].id
        to_id = board.workflow_statuses[1].id
        board.add_workflow_transition(from_status_id=from_id, to_status_id=to_id, name="Start")
        transition_id = board.workflow_transitions[0].id
        board.remove_workflow_transition(transition_id=transition_id)
        assert len(board.workflow_transitions) == 0

    def test_remove_workflow_transition_emits_event(self, board: Board) -> None:
        from_id = board.workflow_statuses[0].id
        to_id = board.workflow_statuses[1].id
        board.add_workflow_transition(from_status_id=from_id, to_status_id=to_id, name="Start")
        transition_id = board.workflow_transitions[0].id
        board.clear_domain_events()
        board.remove_workflow_transition(transition_id=transition_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, WorkflowTransitionRemoved) for e in events)

    def test_remove_nonexistent_workflow_transition_raises(self, board: Board) -> None:
        with pytest.raises(ValueError):
            board.remove_workflow_transition(transition_id=Id.generate())


# ═══════════════════════════════════════════════════════════════════════════
# Views
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardViews:
    def test_create_view(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        assert len(board.views) == 1

    def test_create_view_emits_event(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        events = board.clear_domain_events()
        assert any(isinstance(e, ProjectViewCreated) for e in events)

    def test_update_view(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        view_id = board.views[0].id
        new_config = ProjectViewConfig(view_type=ViewType.LIST)
        board.update_view(view_id=view_id, config=new_config, name="Updated View")
        assert board.views[0].name == "Updated View"
        assert board.views[0].config.view_type == ViewType.LIST

    def test_update_view_emits_event(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        view_id = board.views[0].id
        board.clear_domain_events()
        board.update_view(view_id=view_id, name="Updated")
        events = board.clear_domain_events()
        assert any(isinstance(e, ProjectViewUpdated) for e in events)

    def test_delete_view(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        view_id = board.views[0].id
        board.delete_view(view_id=view_id)
        assert len(board.views) == 0

    def test_delete_view_emits_event(self, board: Board) -> None:
        config = ProjectViewConfig(view_type=ViewType.BOARD)
        board.create_view(name="My View", config=config)
        view_id = board.views[0].id
        board.clear_domain_events()
        board.delete_view(view_id=view_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, ProjectViewDeleted) for e in events)

    def test_update_nonexistent_view_raises(self, board: Board) -> None:
        with pytest.raises(ValueError):
            board.update_view(view_id=Id.generate(), name="X")

    def test_delete_nonexistent_view_raises(self, board: Board) -> None:
        with pytest.raises(ValueError):
            board.delete_view(view_id=Id.generate())


# ═══════════════════════════════════════════════════════════════════════════
# Automation
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBoardAutomation:
    def test_add_automation_rule(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        assert len(board.automation_rules) == 1

    def test_add_automation_rule_emits_event(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        events = board.clear_domain_events()
        assert any(isinstance(e, AutomationRuleCreated) for e in events)

    def test_update_automation_rule(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        rule_id = board.automation_rules[0].id
        board.update_automation_rule(rule_id=rule_id, is_enabled=False)
        assert not board.automation_rules[0].is_enabled

    def test_update_automation_rule_emits_event(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        rule_id = board.automation_rules[0].id
        board.clear_domain_events()
        board.update_automation_rule(rule_id=rule_id, is_enabled=False)
        events = board.clear_domain_events()
        assert any(isinstance(e, AutomationRuleUpdated) for e in events)

    def test_remove_automation_rule(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        rule_id = board.automation_rules[0].id
        board.remove_automation_rule(rule_id=rule_id)
        assert len(board.automation_rules) == 0

    def test_remove_automation_rule_emits_event(self, board: Board) -> None:
        board.add_automation_rule(
            name="Auto-assign",
            trigger=AutomationTrigger.STATUS_CHANGED,
            action=AutomationAction.ASSIGN_USER,
        )
        rule_id = board.automation_rules[0].id
        board.clear_domain_events()
        board.remove_automation_rule(rule_id=rule_id)
        events = board.clear_domain_events()
        assert any(isinstance(e, AutomationRuleDeleted) for e in events)

    def test_update_nonexistent_automation_rule_raises(self, board: Board) -> None:
        with pytest.raises(ValueError):
            board.update_automation_rule(rule_id=Id.generate(), is_enabled=False)

    def test_remove_nonexistent_automation_rule_raises(self, board: Board) -> None:
        with pytest.raises(ValueError):
            board.remove_automation_rule(rule_id=Id.generate())
