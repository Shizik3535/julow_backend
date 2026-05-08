from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.infrastructure.persistence.mappers.file_mapper import FileMapper
from app.context.filestorage.infrastructure.persistence.orm_models.file_orm import (
    FileORM,
    FileShareLinkORM,
    FileTagORM,
)


class SqlFileRepository(
    SqlAlchemyRepository[File, FileORM],
    FileRepository,
):
    """SQLAlchemy-реализация FileRepository."""

    def __init__(self, session: AsyncSession, mapper: FileMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=FileORM)
        self._mapper: FileMapper = mapper

    async def update(self, aggregate: File) -> File:
        """Перезаписать скалярные поля + дочерние коллекции."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(FileORM).where(FileORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            raise EntityNotFoundException(entity_type="File", id=aggregate.id)

        orm.name = aggregate.name
        orm.original_name = aggregate.original_name
        orm.file_type = aggregate.file_type.value
        orm.size_bytes = aggregate.size.value
        orm.mime_type = aggregate.mime_type
        orm.storage_id = self._mapper._map_uuid(aggregate.storage_id)
        orm.storage_path = aggregate.storage_path
        orm.folder_id = (
            self._mapper._map_uuid(aggregate.folder_id) if aggregate.folder_id else None
        )
        orm.uploader_id = self._mapper._map_uuid(aggregate.uploader_id)
        orm.workspace_id = self._mapper._map_uuid(aggregate.workspace_id)
        orm.owner_id = self._mapper._map_uuid(aggregate.owner_id)
        orm.description = aggregate.description
        orm.scan_status = aggregate.scan_status.value
        orm.status = aggregate.status.value
        orm.preview_path = aggregate.preview_path
        orm.is_shared = aggregate.is_shared
        orm.lock_locked_by = (
            self._mapper._map_uuid(aggregate.lock.locked_by) if aggregate.lock else None
        )
        orm.lock_locked_at = aggregate.lock.locked_at if aggregate.lock else None
        orm.lock_expires_at = aggregate.lock.expires_at if aggregate.lock else None
        orm.lock_reason = aggregate.lock.reason if aggregate.lock else None
        orm.updated_at = aggregate.updated_at

        orm.versions = [
            self._mapper._version_to_orm(v, aggregate.id) for v in aggregate.versions
        ]
        orm.permissions = [
            self._mapper._permission_to_orm(p, aggregate.id)
            for p in aggregate.permissions
        ]
        orm.tags = [self._mapper._tag_to_orm(t, aggregate.id) for t in aggregate.tags]
        orm.share_links = [
            self._mapper._share_link_to_orm(l, aggregate.id) for l in aggregate.share_links
        ]
        await self._session.flush()
        return aggregate

    # --- FileRepository methods ---

    async def get_by_workspace(self, workspace_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.workspace_id == self._mapper._map_uuid(workspace_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_folder(self, folder_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.folder_id == self._mapper._map_uuid(folder_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_uploader(self, uploader_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.uploader_id == self._mapper._map_uuid(uploader_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_owner(self, owner_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.owner_id == self._mapper._map_uuid(owner_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_trashed_by_workspace(self, workspace_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FileORM.status == FileStatus.TRASHED.value,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search_by_name(self, query: str, workspace_id: Id) -> list[File]:
        # Экранируем LIKE-метасимволы, чтобы пользовательский ввод не интерпретировался
        # как wildcard-паттерн.
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = select(FileORM).where(
            FileORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FileORM.name.ilike(f"%{escaped}%", escape="\\"),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_tag(self, tag_name: str, workspace_id: Id) -> list[File]:
        stmt = (
            select(FileORM)
            .join(FileTagORM, FileTagORM.file_id == FileORM.id)
            .where(
                FileORM.workspace_id == self._mapper._map_uuid(workspace_id),
                FileTagORM.name == tag_name,
            )
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().unique().all()]

    async def get_by_type(self, file_type: FileType, workspace_id: Id) -> list[File]:
        stmt = select(FileORM).where(
            FileORM.workspace_id == self._mapper._map_uuid(workspace_id),
            FileORM.file_type == file_type.value,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def count_by_workspace(self, workspace_id: Id) -> int:
        stmt = (
            select(func.count())
            .select_from(FileORM)
            .where(FileORM.workspace_id == self._mapper._map_uuid(workspace_id))
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def sum_size_by_workspace(self, workspace_id: Id) -> int:
        stmt = (
            select(func.coalesce(func.sum(FileORM.size_bytes), 0))
            .where(FileORM.workspace_id == self._mapper._map_uuid(workspace_id))
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def get_by_share_token(self, token: str) -> File | None:
        """Найти файл по токену публичной ссылки (для AccessShareLink)."""
        stmt = (
            select(FileORM)
            .join(FileShareLinkORM, FileShareLinkORM.file_id == FileORM.id)
            .where(FileShareLinkORM.token == token)
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return self._mapper.to_domain(orm) if orm else None
