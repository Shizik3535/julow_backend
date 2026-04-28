from __future__ import annotations

import uuid

from datetime import date as date_type
from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.infrastructure.persistence.mappers.project_mapper import ProjectMapper
from app.context.project.infrastructure.persistence.orm_models.project_orm import (
    MilestoneORM,
    ProjectCustomFieldORM,
    ProjectORM,
    project_owners_table,
)


class SqlProjectRepository(
    SqlAlchemyRepository[Project, ProjectORM],
    ProjectRepository,
):
    """SQLAlchemy-реализация ProjectRepository."""

    def __init__(self, session: AsyncSession, mapper: ProjectMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ProjectORM)

    # ------------------------------------------------------------------
    # Override get_by_id — owner_ids через association table
    # ------------------------------------------------------------------

    async def get_by_id(self, id: Id) -> Project | None:
        uuid_val = self._mapper._map_uuid(id)
        stmt = select(ProjectORM).where(ProjectORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            return None
        return await self._to_domain_with_owners(orm_model)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_workspace(self, workspace_id: Id) -> list[Project]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(ProjectORM).where(ProjectORM.workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]

    async def get_by_member(self, user_id: Id) -> list[Project]:
        from app.context.project.infrastructure.persistence.orm_models.project_membership_orm import (
            ProjectMemberORM,
            ProjectMembershipORM,
        )

        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(ProjectORM)
            .join(ProjectMembershipORM, ProjectMembershipORM.project_id == ProjectORM.id)
            .join(ProjectMemberORM, ProjectMemberORM.membership_id == ProjectMembershipORM.id)
            .where(ProjectMemberORM.user_id == user_uuid, ProjectMemberORM.is_active.is_(True))
        )
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]

    async def get_by_methodology(self, methodology: str) -> list[Project]:
        stmt = select(ProjectORM).where(ProjectORM.methodology == methodology)
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]

    async def get_archived_by_workspace(self, workspace_id: Id) -> list[Project]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(ProjectORM).where(
            ProjectORM.workspace_id == uuid_val,
            ProjectORM.status == "archived",
        )
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]

    async def search(self, offset: int = 0, limit: int = 100, filters: dict | None = None) -> list[Project]:
        stmt = select(ProjectORM)
        if filters:
            search_text = filters.get("query") or filters.get("search_text")
            if search_text:
                stmt = stmt.where(ProjectORM.name.ilike(f"%{search_text}%"))
            workspace_id = filters.get("workspace_id")
            if workspace_id is not None:
                uuid_val = self._mapper._map_uuid(Id.from_string(str(workspace_id)))
                stmt = stmt.where(ProjectORM.workspace_id == uuid_val)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]

    # ------------------------------------------------------------------
    # Helper: load owner_ids from association table
    # ------------------------------------------------------------------

    async def _to_domain_with_owners(self, orm_model: ProjectORM) -> Project:
        """Конвертирует ORM → domain и загружает owner_ids из association table."""
        project = self._mapper.to_domain(orm_model)
        stmt = select(project_owners_table.c.user_id).where(
            project_owners_table.c.project_id == orm_model.id
        )
        result = await self._session.execute(stmt)
        owner_uuids = result.scalars().all()
        project.owner_ids = [Id.from_string(str(uid)) for uid in owner_uuids]
        return project

    # ------------------------------------------------------------------
    # Override add — owner_ids через association table
    # ------------------------------------------------------------------

    async def add(self, aggregate: Project) -> Project:
        orm_model = self._mapper.to_orm(aggregate)
        self._session.add(orm_model)

        # owner_ids → association table
        if aggregate.owner_ids:
            await self._session.flush()  # нужен id проекта
            for owner_id in aggregate.owner_ids:
                await self._session.execute(
                    project_owners_table.insert().values(
                        project_id=orm_model.id,
                        user_id=self._mapper._map_uuid(owner_id),
                    )
                )

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # Override update — скаляры + milestones + custom_fields + owners
    # ------------------------------------------------------------------

    async def update(self, aggregate: Project) -> Project:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(ProjectORM).where(ProjectORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="Project", id=aggregate.id)

        # Скалярные поля
        caps = aggregate.methodology_capabilities
        orm_model.workspace_id = self._mapper._map_uuid(aggregate.workspace_id) if aggregate.workspace_id else None
        orm_model.name = aggregate.name
        orm_model.description_format = aggregate.description.format.value if aggregate.description else None
        orm_model.description_raw = aggregate.description.content if aggregate.description else None
        orm_model.icon = aggregate.icon
        orm_model.color = str(aggregate.color) if aggregate.color else None
        orm_model.category_name = aggregate.category.name if aggregate.category else None
        orm_model.category_color = str(aggregate.category.color) if aggregate.category and aggregate.category.color else None
        orm_model.methodology = aggregate.methodology.value
        orm_model.has_sprints = caps.has_sprints
        orm_model.has_backlog = caps.has_backlog
        orm_model.has_milestones = caps.has_milestones
        orm_model.has_epics = caps.has_epics
        orm_model.has_wip_limits = caps.has_wip_limits
        orm_model.has_velocity = caps.has_velocity
        orm_model.has_retros = caps.has_retros
        orm_model.has_burndown = caps.has_burndown
        orm_model.visibility = aggregate.visibility.value
        orm_model.status = aggregate.status.value
        orm_model.start_date = aggregate.start_date
        orm_model.deadline = aggregate.deadline

        # Milestones — diff
        existing_milestones: dict[uuid.UUID, MilestoneORM] = {
            m.id: m for m in list(orm_model.milestones)
        }
        desired_milestone_ids = {self._mapper._map_uuid(m.id) for m in aggregate.milestones}

        for orm_m in list(orm_model.milestones):
            if orm_m.id not in desired_milestone_ids:
                orm_model.milestones.remove(orm_m)

        for milestone in aggregate.milestones:
            m_uuid = self._mapper._map_uuid(milestone.id)
            if m_uuid in existing_milestones:
                orm_m = existing_milestones[m_uuid]
                orm_m.name = milestone.name
                orm_m.description_format = milestone.description.format.value if milestone.description else None
                orm_m.description_raw = milestone.description.content if milestone.description else None
                orm_m.status = milestone.status.value
                orm_m.due_date = milestone.due_date
                orm_m.completed_at = milestone.completed_at
            else:
                orm_model.milestones.append(self._mapper._milestone_to_orm(milestone, aggregate.id))

        # Custom fields — diff
        existing_fields: dict[uuid.UUID, ProjectCustomFieldORM] = {
            f.id: f for f in list(orm_model.custom_field_definitions)
        }

        # Проще: удалить все и вставить заново (custom fields не имеют стабильных id)
        orm_model.custom_field_definitions.clear()
        for field_def in aggregate.custom_field_definitions:
            orm_model.custom_field_definitions.append(
                self._mapper._custom_field_to_orm(field_def, aggregate.id)
            )

        # Owners — association table: удалить старые, вставить новые
        await self._session.execute(
            project_owners_table.delete().where(project_owners_table.c.project_id == uuid_val)
        )
        for owner_id in aggregate.owner_ids:
            await self._session.execute(
                project_owners_table.insert().values(
                    project_id=uuid_val,
                    user_id=self._mapper._map_uuid(owner_id),
                )
            )

        await self._session.flush()
        return aggregate

    async def get_projects_with_upcoming_deadline(self, within_hours: int) -> list[Project]:
        """Найти проекты с дедлайном в ближайшие N часов (не архивированные, активные)."""
        now = datetime.now(tz=None)
        deadline_limit = now + timedelta(hours=within_hours)

        stmt = select(ProjectORM).where(
            and_(
                ProjectORM.deadline.isnot(None),
                ProjectORM.deadline <= deadline_limit.date(),
                ProjectORM.deadline >= date_type.today(),
                ProjectORM.status != "archived",
            )
        )
        result = await self._session.execute(stmt)
        return [await self._to_domain_with_owners(orm) for orm in result.scalars().all()]
