from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.infrastructure.persistence.mappers.board_mapper import BoardMapper
from app.context.project.infrastructure.persistence.orm_models.board_orm import (
    AutomationRuleORM,
    BoardColumnORM,
    BoardORM,
    ProjectViewORM,
    SwimlaneORM,
    WorkflowStatusORM,
    WorkflowTransitionORM,
)


class SqlBoardRepository(
    SqlAlchemyRepository[Board, BoardORM],
    BoardRepository,
):
    """SQLAlchemy-реализация BoardRepository."""

    def __init__(self, session: AsyncSession, mapper: BoardMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=BoardORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_project_id(self, project_id: Id) -> Board | None:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(BoardORM).where(BoardORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    # ------------------------------------------------------------------
    # Override update — 6 дочерних коллекций
    # ------------------------------------------------------------------

    async def update(self, aggregate: Board) -> Board:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(BoardORM).where(BoardORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Board", id=aggregate.id)

        # Скалярные поля
        orm_model.project_id = self._mapper._map_uuid(aggregate.project_id)

        # Columns — diff
        self._sync_child_collection(
            orm_model.columns,
            aggregate.columns,
            lambda c: self._mapper._column_to_orm(c, aggregate.id),
            lambda orm, c: self._update_column_orm(orm, c),
        )

        # Swimlanes — diff
        self._sync_child_collection(
            orm_model.swimlanes,
            aggregate.swimlanes,
            lambda s: self._mapper._swimlane_to_orm(s, aggregate.id),
            lambda orm, s: self._update_swimlane_orm(orm, s),
        )

        # Workflow statuses — diff
        self._sync_child_collection(
            orm_model.workflow_statuses,
            aggregate.workflow_statuses,
            lambda s: self._mapper._workflow_status_to_orm(s, aggregate.id),
            lambda orm, s: self._update_workflow_status_orm(orm, s),
        )

        # Workflow transitions — diff
        self._sync_child_collection(
            orm_model.workflow_transitions,
            aggregate.workflow_transitions,
            lambda t: self._mapper._workflow_transition_to_orm(t, aggregate.id),
            lambda orm, t: self._update_workflow_transition_orm(orm, t),
        )

        # Views — diff
        self._sync_child_collection(
            orm_model.views,
            aggregate.views,
            lambda v: self._mapper._project_view_to_orm(v, aggregate.id),
            lambda orm, v: self._update_project_view_orm(orm, v),
        )

        # Automation rules — diff
        self._sync_child_collection(
            orm_model.automation_rules,
            aggregate.automation_rules,
            lambda r: self._mapper._automation_rule_to_orm(r, aggregate.id),
            lambda orm, r: self._update_automation_rule_orm(orm, r),
        )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Helpers — универсальный diff для дочерних коллекций
    # ------------------------------------------------------------------

    def _sync_child_collection(self, orm_list, domain_list, to_orm, update_orm):
        """Синхронизирует ORM-список с доменным списком по id."""
        existing_by_id: dict[uuid.UUID, object] = {o.id: o for o in list(orm_list)}
        desired_ids = {self._mapper._map_uuid(c.id) for c in domain_list}

        # Удаление убранных
        for orm_item in list(orm_list):
            if orm_item.id not in desired_ids:
                orm_list.remove(orm_item)

        # Обновление существующих + вставка новых
        for child in domain_list:
            child_uuid = self._mapper._map_uuid(child.id)
            if child_uuid in existing_by_id:
                update_orm(existing_by_id[child_uuid], child)
            else:
                orm_list.append(to_orm(child))

    # --- Column update ---

    def _update_column_orm(self, orm: BoardColumnORM, col) -> None:
        orm.name = col.name
        orm.order = col.order
        orm.color = str(col.color) if col.color else None
        orm.wip_limit = col.wip_limit.value if col.wip_limit else None
        orm.status_mapping = self._mapper._map_uuid(col.status_mapping) if col.status_mapping else None

    # --- Swimlane update ---

    def _update_swimlane_orm(self, orm: SwimlaneORM, sl) -> None:
        orm.name = sl.name
        orm.order = sl.order
        orm.group_by = sl.group_by.value
        orm.group_value = sl.group_value

    # --- WorkflowStatus update ---

    def _update_workflow_status_orm(self, orm: WorkflowStatusORM, status) -> None:
        orm.name = status.name
        orm.color = str(status.color) if status.color else None
        orm.icon = status.icon
        orm.order = status.order
        orm.is_default = status.is_default
        orm.category = status.category.value

    # --- WorkflowTransition update ---

    def _update_workflow_transition_orm(self, orm: WorkflowTransitionORM, t) -> None:
        orm.from_status_id = self._mapper._map_uuid(t.from_status_id)
        orm.to_status_id = self._mapper._map_uuid(t.to_status_id)
        orm.name = t.name
        orm.trigger = t.trigger.value if t.trigger else None
        orm.required_permission = t.required_permission

    # --- ProjectView update ---

    def _update_project_view_orm(self, orm: ProjectViewORM, view) -> None:
        orm.name = view.name
        orm.config = view.config.to_dict()
        orm.is_default = view.is_default
        orm.is_shared = view.is_shared
        orm.owner_id = self._mapper._map_uuid(view.owner_id) if view.owner_id else None

    # --- AutomationRule update ---

    def _update_automation_rule_orm(self, orm: AutomationRuleORM, rule) -> None:
        orm.name = rule.name
        orm.trigger = rule.trigger.value
        orm.action = rule.action.value
        orm.action_params = rule.action_params
        orm.is_enabled = rule.is_enabled
