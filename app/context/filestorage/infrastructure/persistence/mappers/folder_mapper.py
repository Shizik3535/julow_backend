from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.entities.file_permission_entry import FilePermissionEntry
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel
from app.context.filestorage.domain.value_objects.folder_type import FolderType
from app.context.filestorage.infrastructure.persistence.orm_models.folder_orm import (
    FolderORM,
    FolderPermissionEntryORM,
)


class FolderMapper(BaseMapper[Folder, FolderORM]):
    """Data Mapper: Folder ↔ FolderORM."""

    def to_domain(self, orm_model: FolderORM) -> Folder:
        permissions = [
            FilePermissionEntry(
                id=self._map_id(p.id),
                user_id=self._map_id(p.user_id) if p.user_id else None,
                team_id=self._map_id(p.team_id) if p.team_id else None,
                access_level=FileAccessLevel(p.access_level),
                granted_by=self._map_id(p.granted_by),
                granted_at=p.granted_at,
            )
            for p in (orm_model.permissions or [])
        ]
        return Folder(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            folder_type=FolderType(orm_model.folder_type),
            parent_folder_id=(
                self._map_id(orm_model.parent_folder_id)
                if orm_model.parent_folder_id
                else None
            ),
            color=Color(value=orm_model.color) if orm_model.color else None,
            description=orm_model.description,
            icon=orm_model.icon,
            owner_id=self._map_id(orm_model.owner_id),
            workspace_id=self._map_id(orm_model.workspace_id),
            project_id=(
                self._map_id(orm_model.project_id) if orm_model.project_id else None
            ),
            is_pinned=orm_model.is_pinned,
            is_shared=orm_model.is_shared,
            is_deleted=orm_model.is_deleted,
            permissions=permissions,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Folder) -> FolderORM:
        orm = FolderORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            folder_type=aggregate.folder_type.value,
            parent_folder_id=(
                self._map_uuid(aggregate.parent_folder_id)
                if aggregate.parent_folder_id
                else None
            ),
            color=aggregate.color.value if aggregate.color else None,
            description=aggregate.description,
            icon=aggregate.icon,
            owner_id=self._map_uuid(aggregate.owner_id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            project_id=self._map_uuid(aggregate.project_id) if aggregate.project_id else None,
            is_pinned=aggregate.is_pinned,
            is_shared=aggregate.is_shared,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.permissions = [
            self._permission_to_orm(p, aggregate.id) for p in aggregate.permissions
        ]
        return orm

    def _permission_to_orm(
        self, p: FilePermissionEntry, folder_id: Id
    ) -> FolderPermissionEntryORM:
        return FolderPermissionEntryORM(
            id=self._map_uuid(p.id),
            folder_id=self._map_uuid(folder_id),
            user_id=self._map_uuid(p.user_id) if p.user_id else None,
            team_id=self._map_uuid(p.team_id) if p.team_id else None,
            access_level=p.access_level.value,
            granted_by=self._map_uuid(p.granted_by),
            granted_at=p.granted_at,
        )
