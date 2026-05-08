from __future__ import annotations

from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.entities.file_lock import FileLock
from app.context.filestorage.domain.entities.file_permission_entry import FilePermissionEntry
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.entities.file_version import FileVersion
from app.context.filestorage.domain.entities.public_share_link import PublicShareLink
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel
from app.context.filestorage.domain.value_objects.file_size import FileSize
from app.context.filestorage.domain.value_objects.file_status import FileStatus
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.virus_scan_status import VirusScanStatus
from app.context.filestorage.infrastructure.persistence.orm_models.file_orm import (
    FileORM,
    FilePermissionEntryORM,
    FileShareLinkORM,
    FileTagORM,
    FileVersionORM,
)


class FileMapper(BaseMapper[File, FileORM]):
    """Data Mapper: File ↔ FileORM."""

    def to_domain(self, orm_model: FileORM) -> File:
        versions = [
            FileVersion(
                id=self._map_id(v.id),
                version_number=v.version_number,
                storage_path=v.storage_path,
                size_bytes=v.size_bytes,
                uploader_id=self._map_id(v.uploader_id),
                change_summary=v.change_summary,
                uploaded_at=v.uploaded_at,
            )
            for v in (orm_model.versions or [])
        ]
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
        tags = [
            FileTag(
                id=self._map_id(t.id),
                name=t.name,
                color=Color(value=t.color) if t.color else None,
            )
            for t in (orm_model.tags or [])
        ]
        share_links = [
            PublicShareLink(
                id=self._map_id(l.id),
                token=l.token,
                password_hash=l.password_hash,
                expires_at=l.expires_at,
                access_level=FileAccessLevel(l.access_level),
                allow_download=l.allow_download,
                max_uses=l.max_uses,
                current_uses=l.current_uses,
                created_by=self._map_id(l.created_by),
                created_at=l.link_created_at,
            )
            for l in (orm_model.share_links or [])
        ]

        lock: FileLock | None = None
        if orm_model.lock_locked_by is not None and orm_model.lock_locked_at is not None:
            lock = FileLock(
                locked_by=self._map_id(orm_model.lock_locked_by),
                locked_at=orm_model.lock_locked_at,
                expires_at=orm_model.lock_expires_at,
                reason=orm_model.lock_reason,
            )

        return File(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            original_name=orm_model.original_name,
            file_type=FileType(orm_model.file_type),
            size=FileSize(value=orm_model.size_bytes),
            mime_type=orm_model.mime_type,
            storage_id=self._map_id(orm_model.storage_id),
            storage_path=orm_model.storage_path,
            folder_id=self._map_id(orm_model.folder_id) if orm_model.folder_id else None,
            uploader_id=self._map_id(orm_model.uploader_id),
            workspace_id=self._map_id(orm_model.workspace_id),
            owner_id=self._map_id(orm_model.owner_id),
            description=orm_model.description,
            scan_status=VirusScanStatus(orm_model.scan_status),
            status=FileStatus(orm_model.status),
            permissions=permissions,
            versions=versions,
            lock=lock,
            tags=tags,
            share_links=share_links,
            preview_path=orm_model.preview_path,
            is_shared=orm_model.is_shared,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: File) -> FileORM:
        orm = FileORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            original_name=aggregate.original_name,
            file_type=aggregate.file_type.value,
            size_bytes=aggregate.size.value,
            mime_type=aggregate.mime_type,
            storage_id=self._map_uuid(aggregate.storage_id),
            storage_path=aggregate.storage_path,
            folder_id=self._map_uuid(aggregate.folder_id) if aggregate.folder_id else None,
            uploader_id=self._map_uuid(aggregate.uploader_id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            owner_id=self._map_uuid(aggregate.owner_id),
            description=aggregate.description,
            scan_status=aggregate.scan_status.value,
            status=aggregate.status.value,
            preview_path=aggregate.preview_path,
            is_shared=aggregate.is_shared,
            lock_locked_by=(
                self._map_uuid(aggregate.lock.locked_by) if aggregate.lock else None
            ),
            lock_locked_at=aggregate.lock.locked_at if aggregate.lock else None,
            lock_expires_at=aggregate.lock.expires_at if aggregate.lock else None,
            lock_reason=aggregate.lock.reason if aggregate.lock else None,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.versions = [self._version_to_orm(v, aggregate.id) for v in aggregate.versions]
        orm.permissions = [
            self._permission_to_orm(p, aggregate.id) for p in aggregate.permissions
        ]
        orm.tags = [self._tag_to_orm(t, aggregate.id) for t in aggregate.tags]
        orm.share_links = [
            self._share_link_to_orm(l, aggregate.id) for l in aggregate.share_links
        ]
        return orm

    def _version_to_orm(self, v: FileVersion, file_id: Id) -> FileVersionORM:
        return FileVersionORM(
            id=self._map_uuid(v.id),
            file_id=self._map_uuid(file_id),
            version_number=v.version_number,
            storage_path=v.storage_path,
            size_bytes=v.size_bytes,
            uploader_id=self._map_uuid(v.uploader_id),
            change_summary=v.change_summary,
            uploaded_at=v.uploaded_at,
        )

    def _permission_to_orm(
        self, p: FilePermissionEntry, file_id: Id
    ) -> FilePermissionEntryORM:
        return FilePermissionEntryORM(
            id=self._map_uuid(p.id),
            file_id=self._map_uuid(file_id),
            user_id=self._map_uuid(p.user_id) if p.user_id else None,
            team_id=self._map_uuid(p.team_id) if p.team_id else None,
            access_level=p.access_level.value,
            granted_by=self._map_uuid(p.granted_by),
            granted_at=p.granted_at,
        )

    def _tag_to_orm(self, t: FileTag, file_id: Id) -> FileTagORM:
        return FileTagORM(
            id=self._map_uuid(t.id),
            file_id=self._map_uuid(file_id),
            name=t.name,
            color=t.color.value if t.color else None,
        )

    def _share_link_to_orm(self, l: PublicShareLink, file_id: Id) -> FileShareLinkORM:
        return FileShareLinkORM(
            id=self._map_uuid(l.id),
            file_id=self._map_uuid(file_id),
            token=l.token,
            password_hash=l.password_hash,
            expires_at=l.expires_at,
            access_level=l.access_level.value,
            allow_download=l.allow_download,
            max_uses=l.max_uses,
            current_uses=l.current_uses,
            created_by=self._map_uuid(l.created_by),
            link_created_at=l.created_at,
        )
