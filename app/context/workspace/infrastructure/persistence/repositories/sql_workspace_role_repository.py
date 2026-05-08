from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.context.workspace.infrastructure.persistence.mappers.workspace_role_mapper import WorkspaceRoleMapper
from app.context.workspace.infrastructure.persistence.orm_models.workspace_role_orm import WorkspaceRoleORM


class SqlWorkspaceRoleRepository(SqlAlchemyRepository[WorkspaceRole, WorkspaceRoleORM], WorkspaceRoleRepository):
    """SQLAlchemy-реализация WorkspaceRoleRepository."""

    def __init__(self, session: AsyncSession, mapper: WorkspaceRoleMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=WorkspaceRoleORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_name(self, name: str) -> WorkspaceRole | None:
        stmt = select(WorkspaceRoleORM).where(WorkspaceRoleORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_system_roles(self) -> list[WorkspaceRole]:
        stmt = select(WorkspaceRoleORM).where(WorkspaceRoleORM.is_system.is_(True))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_workspace(self, workspace_id: Id) -> list[WorkspaceRole]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        # Системные роли (workspace_id IS NULL) + кастомные для workspace
        stmt = select(WorkspaceRoleORM).where(
            or_(WorkspaceRoleORM.workspace_id.is_(None), WorkspaceRoleORM.workspace_id == uuid_val)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[WorkspaceRole]:
        stmt = select(WorkspaceRoleORM)
        if filters:
            name = filters.get("name")
            if name:
                safe = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                stmt = stmt.where(WorkspaceRoleORM.name.ilike(f"%{safe}%", escape="\\"))
            is_system = filters.get("is_system")
            if is_system is not None:
                stmt = stmt.where(WorkspaceRoleORM.is_system == is_system)
            workspace_id = filters.get("workspace_id")
            if workspace_id:
                stmt = stmt.where(WorkspaceRoleORM.workspace_id == workspace_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]
