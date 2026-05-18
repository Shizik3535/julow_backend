from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
from app.context.project.domain.value_objects.automation_action import AutomationAction
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.domain.entities.board_column import BoardColumn
from app.context.project.domain.entities.swimlane import Swimlane
from app.context.project.domain.entities.workflow_status import WorkflowStatus
from app.context.project.domain.entities.workflow_transition import WorkflowTransition
from app.context.project.domain.entities.project_view import ProjectView
from app.context.project.domain.entities.automation_rule import AutomationRule
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
    WIPLimitExceededException,
)


@dataclass
class Board(AggregateRoot):
    """
    Корень агрегата доски проекта (Project BC).

    Доска — колонки, swimlanes, workflow, views, автоматизации.
    Отдельный AR для масштабируемости.

    Атрибуты:
        project_id: Opaque ID проекта.
        columns: Список колонок.
        swimlanes: Список swimlanes.
        workflow_statuses: Список статусов workflow.
        workflow_transitions: Список переходов workflow.
        views: Список представлений.
        automation_rules: Список правил автоматизации.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id = field(default_factory=Id.generate)
    columns: list[BoardColumn] = field(default_factory=list)
    swimlanes: list[Swimlane] = field(default_factory=list)
    workflow_statuses: list[WorkflowStatus] = field(default_factory=list)
    workflow_transitions: list[WorkflowTransition] = field(default_factory=list)
    views: list[ProjectView] = field(default_factory=list)
    automation_rules: list[AutomationRule] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, project_id: Id, methodology: Methodology) -> Board:
        """Создаёт доску с дефолтными колонками и статусами по методологии."""
        board = cls(project_id=project_id)

        # Дефолтные статусы (4 колонки: To Do / In Progress / Review / Done).
        # Категории матчатся с фронтенд-ключами (todo/in_progress/review/done).
        todo = WorkflowStatus(name="To Do", order=0, is_default=True, category=WorkflowStatusCategory.TODO)
        in_progress = WorkflowStatus(name="In Progress", order=1, category=WorkflowStatusCategory.IN_PROGRESS)
        review = WorkflowStatus(name="Review", order=2, category=WorkflowStatusCategory.REVIEW)
        done = WorkflowStatus(name="Done", order=3, category=WorkflowStatusCategory.DONE)
        board.workflow_statuses = [todo, in_progress, review, done]

        # Дефолтные колонки
        board.columns = [
            BoardColumn(name="To Do", order=0, status_mapping=todo.id),
            BoardColumn(name="In Progress", order=1, status_mapping=in_progress.id),
            BoardColumn(name="Review", order=2, status_mapping=review.id),
            BoardColumn(name="Done", order=3, status_mapping=done.id),
        ]

        return board

    # --- Колонки ---

    def add_column(self, name: str, color: Color | None = None, wip_limit: WIPLimit | None = None, status_mapping: Id | None = None) -> None:
        order = len(self.columns)
        column = BoardColumn(name=name, order=order, color=color, wip_limit=wip_limit, status_mapping=status_mapping)
        self.columns.append(column)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            BoardColumnAdded(project_id=str(self.project_id), column_id=str(column.id), name=name)
        )

    def remove_column(self, column_id: Id) -> None:
        column = next((c for c in self.columns if c.id == column_id), None)
        if column is None:
            raise BoardColumnNotFoundException(id=column_id)
        self.columns.remove(column)
        self._reorder_columns()
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            BoardColumnRemoved(project_id=str(self.project_id), column_id=str(column_id))
        )

    def reorder_columns(self, column_ids: list[Id]) -> None:
        """Переупорядочивает колонки по списку ID."""
        col_map = {c.id: c for c in self.columns}
        reordered = []
        for i, cid in enumerate(column_ids):
            if cid in col_map:
                col_map[cid].order = i
                reordered.append(col_map[cid])
        self.columns = reordered
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(BoardColumnReordered(project_id=str(self.project_id)))

    def _reorder_columns(self) -> None:
        for i, col in enumerate(self.columns):
            col.order = i

    def change_wip_limit(self, column_id: Id, wip_limit: WIPLimit | None) -> None:
        column = next((c for c in self.columns if c.id == column_id), None)
        if column is None:
            raise BoardColumnNotFoundException(id=column_id)
        column.wip_limit = wip_limit
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WIPLimitChanged(project_id=str(self.project_id), column_id=str(column_id))
        )

    # --- Swimlanes ---

    def add_swimlane(self, name: str, group_by: SwimlaneGroupBy, group_value: str | None = None) -> None:
        order = len(self.swimlanes)
        swimlane = Swimlane(name=name, order=order, group_by=group_by, group_value=group_value)
        self.swimlanes.append(swimlane)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SwimlaneAdded(project_id=str(self.project_id), swimlane_id=str(swimlane.id))
        )

    def remove_swimlane(self, swimlane_id: Id) -> None:
        swimlane = next((s for s in self.swimlanes if s.id == swimlane_id), None)
        if swimlane is None:
            raise SwimlaneNotFoundException(id=swimlane_id)
        self.swimlanes.remove(swimlane)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SwimlaneRemoved(project_id=str(self.project_id), swimlane_id=str(swimlane_id))
        )

    # --- Workflow ---

    def add_workflow_status(self, name: str, color: Color | None = None, icon: str | None = None, category: WorkflowStatusCategory = WorkflowStatusCategory.TODO, is_default: bool = False) -> None:
        order = len(self.workflow_statuses)
        status = WorkflowStatus(name=name, color=color, icon=icon, order=order, is_default=is_default, category=category)
        self.workflow_statuses.append(status)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkflowStatusAdded(
                project_id=str(self.project_id),
                status_id=str(status.id),
                name=name,
                category=category.value,
            )
        )

    def remove_workflow_status(self, status_id: Id) -> None:
        status = next((s for s in self.workflow_statuses if s.id == status_id), None)
        if status is None:
            raise WorkflowStatusNotFoundException(id=status_id)
        self.workflow_statuses.remove(status)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkflowStatusRemoved(project_id=str(self.project_id), status_id=str(status_id))
        )

    def add_workflow_transition(self, from_status_id: Id, to_status_id: Id, name: str, required_permission: str | None = None) -> None:
        transition = WorkflowTransition(
            from_status_id=from_status_id,
            to_status_id=to_status_id,
            name=name,
            required_permission=required_permission,
        )
        self.workflow_transitions.append(transition)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkflowTransitionAdded(project_id=str(self.project_id), transition_id=str(transition.id))
        )

    def remove_workflow_transition(self, transition_id: Id) -> None:
        transition = next((t for t in self.workflow_transitions if t.id == transition_id), None)
        if transition is None:
            raise ValueError(f"Переход не найден: {transition_id}")
        self.workflow_transitions.remove(transition)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkflowTransitionRemoved(project_id=str(self.project_id), transition_id=str(transition_id))
        )

    # --- Views ---

    def create_view(self, name: str, config: ProjectViewConfig, is_shared: bool = True, owner_id: Id | None = None) -> None:
        view = ProjectView(name=name, config=config, is_shared=is_shared, owner_id=owner_id)
        self.views.append(view)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectViewCreated(project_id=str(self.project_id), view_id=str(view.id))
        )

    def update_view(self, view_id: Id, config: ProjectViewConfig | None = None, name: str | None = None) -> None:
        view = next((v for v in self.views if v.id == view_id), None)
        if view is None:
            raise ValueError(f"Представление не найдено: {view_id}")
        if name is not None:
            view.name = name
        if config is not None:
            view.config = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectViewUpdated(project_id=str(self.project_id), view_id=str(view_id))
        )

    def delete_view(self, view_id: Id) -> None:
        view = next((v for v in self.views if v.id == view_id), None)
        if view is None:
            raise ValueError(f"Представление не найдено: {view_id}")
        self.views.remove(view)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectViewDeleted(project_id=str(self.project_id), view_id=str(view_id))
        )

    # --- Automation ---

    def add_automation_rule(self, name: str, trigger: AutomationTrigger, action: AutomationAction, action_params: dict[str, str] | None = None) -> None:
        rule = AutomationRule(name=name, trigger=trigger, action=action, action_params=action_params or {})
        self.automation_rules.append(rule)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AutomationRuleCreated(project_id=str(self.project_id), rule_id=str(rule.id))
        )

    def update_automation_rule(self, rule_id: Id, is_enabled: bool | None = None, action_params: dict[str, str] | None = None) -> None:
        rule = next((r for r in self.automation_rules if r.id == rule_id), None)
        if rule is None:
            raise ValueError(f"Правило автоматизации не найдено: {rule_id}")
        if is_enabled is not None:
            rule.is_enabled = is_enabled
        if action_params is not None:
            rule.action_params = action_params
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AutomationRuleUpdated(project_id=str(self.project_id), rule_id=str(rule_id))
        )

    def remove_automation_rule(self, rule_id: Id) -> None:
        rule = next((r for r in self.automation_rules if r.id == rule_id), None)
        if rule is None:
            raise ValueError(f"Правило автоматизации не найдено: {rule_id}")
        self.automation_rules.remove(rule)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            AutomationRuleDeleted(project_id=str(self.project_id), rule_id=str(rule_id))
        )
