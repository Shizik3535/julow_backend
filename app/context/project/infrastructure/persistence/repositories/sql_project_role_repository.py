from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.infrastructure.persistence.mappers.project_role_mapper import ProjectRoleMapper
from app.context.project.infrastructure.persistence.orm_models.project_role_orm import ProjectRoleORM


class SqlProjectRoleRepository(
    SqlAlchemyRepository[ProjectRole, ProjectRoleORM],
    ProjectRoleRepository,
):
    """SQLAlchemy-реализация ProjectRoleRepository."""

    def __init__(self, session: AsyncSession, mapper: ProjectRoleMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ProjectRoleORM)

    async def get_by_name(self, name: str) -> ProjectRole | None:
        stmt = select(ProjectRoleORM).where(ProjectRoleORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_system_roles(self) -> list[ProjectRole]:
        stmt = select(ProjectRoleORM).where(ProjectRoleORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_project(self, project_id: Id) -> list[ProjectRole]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(ProjectRoleORM).where(ProjectRoleORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(self, query: str, project_id: Id | None = None) -> list[ProjectRole]:
        safe = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = select(ProjectRoleORM).where(ProjectRoleORM.name.ilike(f"%{safe}%", escape="\\"))
        if project_id is not None:
            uuid_val = self._mapper._map_uuid(project_id)
            stmt = stmt.where(ProjectRoleORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]
