from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository
from app.context.filestorage.domain.value_objects.folder_type import FolderType
from app.context.filestorage.infrastructure.persistence.mappers.folder_mapper import FolderMapper
from app.context.filestorage.infrastructure.persistence.orm_models.folder_orm import FolderORM


class SqlFolderRepository(
    SqlAlchemyRepository[Folder, FolderORM],
    FolderRepository,
):
    """SQLAlchemy-реализация FolderRepository."""

    def __init__(self, session: AsyncSession, mapper: FolderMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=FolderORM)
        self._mapper: FolderMapper = mapper

    async def update(self, aggregate: Folder) -> Folder:
        """Перезаписать скалярные поля + permissions."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(FolderORM).where(FolderORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            raise EntityNotFoundException(entity_type="Folder", id=aggregate.id)

        orm.name = aggregate.name
        orm.folder_type = aggregate.folder_type.value
        orm.parent_folder_id = (
            self._mapper._map_uuid(aggregate.parent_folder_id)
            if aggregate.parent_folder_id
            else None
        )
        orm.color = aggregate.color.value if aggregate.color else None
        orm.description = aggregate.description
        orm.icon = aggregate.icon
        orm.owner_id = self._mapper._map_uuid(aggregate.owner_id)
        orm.workspace_id = self._mapper._map_uuid(aggregate.workspace_id)
        orm.project_id = (
            self._mapper._map_uuid(aggregate.project_id) if aggregate.project_id else None
        )
        orm.is_pinned = aggregate.is_pinned
        orm.is_shared = aggregate.is_shared
        orm.is_deleted = aggregate.is_deleted
        orm.updated_at = aggregate.updated_at
        orm.permissions = [
            self._mapper._permission_to_orm(p, aggregate.id) for p in aggregate.permissions
        ]
        await self._session.flush()
        return aggregate

    async def get_by_workspace(self, workspace_id: Id) -> list[Folder]:
        stmt = select(FolderORM).where(
            FolderORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FolderORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_parent(self, parent_folder_id: Id) -> list[Folder]:
        stmt = select(FolderORM).where(
            FolderORM.parent_folder_id == self._mapper._map_uuid(parent_folder_id),
            FolderORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_root_folders(self, workspace_id: Id) -> list[Folder]:
        stmt = select(FolderORM).where(
            FolderORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FolderORM.parent_folder_id.is_(None),
            FolderORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_project(self, project_id: Id) -> Folder | None:
        stmt = select(FolderORM).where(
            FolderORM.project_id == self._mapper._map_uuid(project_id),
            FolderORM.folder_type == FolderType.PROJECT.value,
            FolderORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_type(
        self, folder_type: FolderType, workspace_id: Id
    ) -> list[Folder]:
        stmt = select(FolderORM).where(
            FolderORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FolderORM.folder_type == folder_type.value,
            FolderORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Folder]:
        stmt = select(FolderORM).where(FolderORM.is_deleted.is_(False))
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
