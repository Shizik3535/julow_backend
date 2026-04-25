from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.entities.board_column import BoardColumn
from app.context.project.domain.entities.swimlane import Swimlane
from app.context.project.domain.entities.workflow_status import WorkflowStatus
from app.context.project.domain.entities.workflow_transition import WorkflowTransition
from app.context.project.domain.entities.project_view import ProjectView
from app.context.project.domain.entities.automation_rule import AutomationRule
from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
from app.context.project.domain.value_objects.automation_action import AutomationAction
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.infrastructure.persistence.orm_models.board_orm import (
    BoardORM,
    BoardColumnORM,
    SwimlaneORM,
    WorkflowStatusORM,
    WorkflowTransitionORM,
    ProjectViewORM,
    AutomationRuleORM,
)


class BoardMapper(BaseMapper[Board, BoardORM]):
    """Data Mapper: Board ↔ BoardORM."""

    def to_domain(self, orm_model: BoardORM) -> Board:
        columns = [self._column_orm_to_domain(c) for c in orm_model.columns]
        swimlanes = [self._swimlane_orm_to_domain(s) for s in orm_model.swimlanes]
        statuses = [self._workflow_status_orm_to_domain(s) for s in orm_model.workflow_statuses]
        transitions = [self._workflow_transition_orm_to_domain(t) for t in orm_model.workflow_transitions]
        views = [self._project_view_orm_to_domain(v) for v in orm_model.views]
        rules = [self._automation_rule_orm_to_domain(r) for r in orm_model.automation_rules]

        return Board(
            id=self._map_id(orm_model.id),
            project_id=self._map_id(orm_model.project_id),
            columns=columns,
            swimlanes=swimlanes,
            workflow_statuses=statuses,
            workflow_transitions=transitions,
            views=views,
            automation_rules=rules,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Board) -> BoardORM:
        orm = BoardORM(
            id=self._map_uuid(aggregate.id),
            project_id=self._map_uuid(aggregate.project_id),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.columns = [self._column_to_orm(c, aggregate.id) for c in aggregate.columns]
        orm.swimlanes = [self._swimlane_to_orm(s, aggregate.id) for s in aggregate.swimlanes]
        orm.workflow_statuses = [self._workflow_status_to_orm(s, aggregate.id) for s in aggregate.workflow_statuses]
        orm.workflow_transitions = [self._workflow_transition_to_orm(t, aggregate.id) for t in aggregate.workflow_transitions]
        orm.views = [self._project_view_to_orm(v, aggregate.id) for v in aggregate.views]
        orm.automation_rules = [self._automation_rule_to_orm(r, aggregate.id) for r in aggregate.automation_rules]
        return orm

    # --- BoardColumn ---

    def _column_orm_to_domain(self, orm: BoardColumnORM) -> BoardColumn:
        wip_limit = WIPLimit(value=orm.wip_limit) if orm.wip_limit is not None else None
        color = Color(orm.color) if orm.color else None
        status_mapping = self._map_id(orm.status_mapping) if orm.status_mapping else None
        return BoardColumn(
            id=self._map_id(orm.id),
            name=orm.name,
            order=orm.order,
            color=color,
            wip_limit=wip_limit,
            status_mapping=status_mapping,
        )

    def _column_to_orm(self, col: BoardColumn, board_id: Id) -> BoardColumnORM:
        return BoardColumnORM(
            id=self._map_uuid(col.id),
            board_id=self._map_uuid(board_id),
            name=col.name,
            order=col.order,
            color=str(col.color) if col.color else None,
            wip_limit=col.wip_limit.value if col.wip_limit else None,
            status_mapping=self._map_uuid(col.status_mapping) if col.status_mapping else None,
        )

    # --- Swimlane ---

    def _swimlane_orm_to_domain(self, orm: SwimlaneORM) -> Swimlane:
        return Swimlane(
            id=self._map_id(orm.id),
            name=orm.name,
            order=orm.order,
            group_by=SwimlaneGroupBy(orm.group_by),
            group_value=orm.group_value,
        )

    def _swimlane_to_orm(self, sl: Swimlane, board_id: Id) -> SwimlaneORM:
        return SwimlaneORM(
            id=self._map_uuid(sl.id),
            board_id=self._map_uuid(board_id),
            name=sl.name,
            order=sl.order,
            group_by=sl.group_by.value,
            group_value=sl.group_value,
        )

    # --- WorkflowStatus ---

    def _workflow_status_orm_to_domain(self, orm: WorkflowStatusORM) -> WorkflowStatus:
        color = Color(orm.color) if orm.color else None
        return WorkflowStatus(
            id=self._map_id(orm.id),
            name=orm.name,
            color=color,
            icon=orm.icon,
            order=orm.order,
            is_default=orm.is_default,
            category=WorkflowStatusCategory(orm.category),
        )

    def _workflow_status_to_orm(self, status: WorkflowStatus, board_id: Id) -> WorkflowStatusORM:
        return WorkflowStatusORM(
            id=self._map_uuid(status.id),
            board_id=self._map_uuid(board_id),
            name=status.name,
            color=str(status.color) if status.color else None,
            icon=status.icon,
            order=status.order,
            is_default=status.is_default,
            category=status.category.value,
        )

    # --- WorkflowTransition ---

    def _workflow_transition_orm_to_domain(self, orm: WorkflowTransitionORM) -> WorkflowTransition:
        trigger = AutomationTrigger(orm.trigger) if orm.trigger else None
        return WorkflowTransition(
            id=self._map_id(orm.id),
            from_status_id=self._map_id(orm.from_status_id),
            to_status_id=self._map_id(orm.to_status_id),
            name=orm.name,
            trigger=trigger,
            required_permission=orm.required_permission,
        )

    def _workflow_transition_to_orm(self, t: WorkflowTransition, board_id: Id) -> WorkflowTransitionORM:
        return WorkflowTransitionORM(
            id=self._map_uuid(t.id),
            board_id=self._map_uuid(board_id),
            from_status_id=self._map_uuid(t.from_status_id),
            to_status_id=self._map_uuid(t.to_status_id),
            name=t.name,
            trigger=t.trigger.value if t.trigger else None,
            required_permission=t.required_permission,
        )

    # --- ProjectView ---

    def _project_view_orm_to_domain(self, orm: ProjectViewORM) -> ProjectView:
        config = ProjectViewConfig.from_dict(orm.config) if orm.config else ProjectViewConfig()
        owner_id = self._map_id(orm.owner_id) if orm.owner_id else None
        return ProjectView(
            id=self._map_id(orm.id),
            name=orm.name,
            config=config,
            is_default=orm.is_default,
            is_shared=orm.is_shared,
            owner_id=owner_id,
        )

    def _project_view_to_orm(self, view: ProjectView, board_id: Id) -> ProjectViewORM:
        return ProjectViewORM(
            id=self._map_uuid(view.id),
            board_id=self._map_uuid(board_id),
            name=view.name,
            config=view.config.to_dict(),
            is_default=view.is_default,
            is_shared=view.is_shared,
            owner_id=self._map_uuid(view.owner_id) if view.owner_id else None,
        )

    # --- AutomationRule ---

    def _automation_rule_orm_to_domain(self, orm: AutomationRuleORM) -> AutomationRule:
        return AutomationRule(
            id=self._map_id(orm.id),
            name=orm.name,
            trigger=AutomationTrigger(orm.trigger),
            action=AutomationAction(orm.action),
            action_params=orm.action_params or {},
            is_enabled=orm.is_enabled,
        )

    def _automation_rule_to_orm(self, rule: AutomationRule, board_id: Id) -> AutomationRuleORM:
        return AutomationRuleORM(
            id=self._map_uuid(rule.id),
            board_id=self._map_uuid(board_id),
            name=rule.name,
            trigger=rule.trigger.value,
            action=rule.action.value,
            action_params=rule.action_params,
            is_enabled=rule.is_enabled,
        )
