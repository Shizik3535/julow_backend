from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.infrastructure.persistence.mappers.workspace_mapper import WorkspaceMapper
from app.context.workspace.infrastructure.persistence.orm_models.workspace_membership_orm import (
    WorkspaceMemberORM,
    WorkspaceMembershipORM,
)
from app.context.workspace.infrastructure.persistence.orm_models.workspace_orm import WorkspaceORM


class SqlWorkspaceRepository(SqlAlchemyRepository[Workspace, WorkspaceORM], WorkspaceRepository):
    """SQLAlchemy-реализация WorkspaceRepository."""

    def __init__(self, session: AsyncSession, mapper: WorkspaceMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=WorkspaceORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_owner(self, owner_id: Id) -> list[Workspace]:
        uuid_val = self._mapper._map_uuid(owner_id)
        # owner_ids хранится как JSON-массив строк UUID
        stmt = select(WorkspaceORM).where(
            WorkspaceORM.owner_ids.bool_op("@>")(str(uuid_val))
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_organization(self, organization_id: Id) -> list[Workspace]:
        uuid_val = self._mapper._map_uuid(organization_id)
        stmt = select(WorkspaceORM).where(WorkspaceORM.organization_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_organization_and_member(
        self, organization_id: Id, user_id: Id
    ) -> list[Workspace]:
        org_uuid = self._mapper._map_uuid(organization_id)
        user_uuid = self._mapper._map_uuid(user_id)
        stmt = (
            select(WorkspaceORM)
            .join(WorkspaceMembershipORM, WorkspaceMembershipORM.workspace_id == WorkspaceORM.id)
            .join(WorkspaceMemberORM, WorkspaceMemberORM.membership_id == WorkspaceMembershipORM.id)
            .where(
                WorkspaceORM.organization_id == org_uuid,
                WorkspaceMemberORM.user_id == user_uuid,
                WorkspaceMemberORM.is_active.is_(True),
            )
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_parent(self, parent_workspace_id: Id) -> list[Workspace]:
        uuid_val = self._mapper._map_uuid(parent_workspace_id)
        stmt = select(WorkspaceORM).where(WorkspaceORM.parent_workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_children(self, workspace_id: Id) -> list[Workspace]:
        return await self.get_by_parent(workspace_id)

    async def get_root_workspaces(self) -> list[Workspace]:
        stmt = select(WorkspaceORM).where(WorkspaceORM.parent_workspace_id.is_(None))
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Workspace]:
        stmt = select(WorkspaceORM)
        if filters:
            name = filters.get("name")
            if name:
                stmt = stmt.where(WorkspaceORM.name.ilike(f"%{name}%"))
            status = filters.get("status")
            if status:
                stmt = stmt.where(WorkspaceORM.status == status)
            organization_id = filters.get("organization_id")
            if organization_id:
                stmt = stmt.where(WorkspaceORM.organization_id == organization_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def count_by_organization(self, organization_id: Id) -> int:
        uuid_val = self._mapper._map_uuid(organization_id)
        stmt = select(func.count()).select_from(WorkspaceORM).where(
            WorkspaceORM.organization_id == uuid_val
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
