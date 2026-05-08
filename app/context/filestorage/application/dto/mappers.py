"""Хелперы преобразования доменных объектов FileStorage BC в DTO."""
from __future__ import annotations

from app.context.filestorage.application.dto.file_dto import (
    FileDTO,
    FileLockDTO,
    FilePermissionEntryDTO,
    FileTagDTO,
    FileVersionDTO,
    PublicShareLinkDTO,
)
from app.context.filestorage.application.dto.folder_dto import FolderDTO
from app.context.filestorage.application.dto.storage_dto import StorageConfigDTO, StorageDTO
from app.context.filestorage.domain.aggregates.file import File
from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.entities.file_lock import FileLock
from app.context.filestorage.domain.entities.file_permission_entry import FilePermissionEntry
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.entities.file_version import FileVersion
from app.context.filestorage.domain.entities.public_share_link import PublicShareLink


def file_version_to_dto(v: FileVersion) -> FileVersionDTO:
    return FileVersionDTO(
        version_number=v.version_number,
        storage_path=v.storage_path,
        size_bytes=v.size_bytes,
        uploader_id=str(v.uploader_id),
        change_summary=v.change_summary,
        uploaded_at=v.uploaded_at,
    )


def permission_entry_to_dto(p: FilePermissionEntry) -> FilePermissionEntryDTO:
    return FilePermissionEntryDTO(
        id=str(p.id),
        user_id=str(p.user_id) if p.user_id else None,
        team_id=str(p.team_id) if p.team_id else None,
        access_level=p.access_level.value,
        granted_by=str(p.granted_by),
        granted_at=p.granted_at,
    )


def share_link_to_dto(l: PublicShareLink) -> PublicShareLinkDTO:
    return PublicShareLinkDTO(
        id=str(l.id),
        token=l.token,
        has_password=l.password_hash is not None,
        expires_at=l.expires_at,
        access_level=l.access_level.value,
        allow_download=l.allow_download,
        max_uses=l.max_uses,
        current_uses=l.current_uses,
        created_by=str(l.created_by),
        created_at=l.created_at,
    )


def file_tag_to_dto(t: FileTag) -> FileTagDTO:
    return FileTagDTO(
        id=str(t.id),
        name=t.name,
        color=t.color.value if t.color else None,
    )


def file_lock_to_dto(lock: FileLock | None) -> FileLockDTO | None:
    if lock is None:
        return None
    return FileLockDTO(
        locked_by=str(lock.locked_by),
        locked_at=lock.locked_at,
        expires_at=lock.expires_at,
        reason=lock.reason,
    )


def file_to_dto(file: File) -> FileDTO:
    return FileDTO(
        id=str(file.id),
        name=file.name,
        original_name=file.original_name,
        file_type=file.file_type.value,
        size_bytes=file.size.value,
        mime_type=file.mime_type,
        storage_id=str(file.storage_id),
        storage_path=file.storage_path,
        folder_id=str(file.folder_id) if file.folder_id else None,
        uploader_id=str(file.uploader_id),
        workspace_id=str(file.workspace_id),
        owner_id=str(file.owner_id),
        description=file.description,
        scan_status=file.scan_status.value,
        status=file.status.value,
        permissions=[permission_entry_to_dto(p) for p in file.permissions],
        versions=[file_version_to_dto(v) for v in file.versions],
        lock=file_lock_to_dto(file.lock),
        tags=[file_tag_to_dto(t) for t in file.tags],
        share_links=[share_link_to_dto(l) for l in file.share_links],
        preview_path=file.preview_path,
        is_shared=file.is_shared,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )


def folder_to_dto(folder: Folder) -> FolderDTO:
    return FolderDTO(
        id=str(folder.id),
        name=folder.name,
        folder_type=folder.folder_type.value,
        parent_folder_id=str(folder.parent_folder_id) if folder.parent_folder_id else None,
        color=folder.color.value if folder.color else None,
        description=folder.description,
        icon=folder.icon,
        owner_id=str(folder.owner_id),
        workspace_id=str(folder.workspace_id),
        project_id=str(folder.project_id) if folder.project_id else None,
        is_pinned=folder.is_pinned,
        is_shared=folder.is_shared,
        permissions=[permission_entry_to_dto(p) for p in folder.permissions],
        created_at=folder.created_at,
        updated_at=folder.updated_at,
    )


def storage_to_dto(storage: Storage) -> StorageDTO:
    used_percent = 0
    if storage.max_bytes > 0:
        used_percent = int(storage.used_bytes / storage.max_bytes * 100)
    return StorageDTO(
        id=str(storage.id),
        owner_type=storage.owner_type.value,
        owner_id=str(storage.owner_id),
        provider=storage.provider.value,
        config=StorageConfigDTO(
            endpoint=storage.config.endpoint,
            bucket=storage.config.bucket,
            region=storage.config.region,
            access_key_ref=storage.config.access_key_ref,
            secret_key_ref=storage.config.secret_key_ref,
            custom_params=storage.config.custom_params,
        ),
        max_bytes=storage.max_bytes,
        used_bytes=storage.used_bytes,
        used_percent=used_percent,
        allowed_file_types=[t.value for t in storage.allowed_file_types] if storage.allowed_file_types else None,
        max_file_size_bytes=storage.max_file_size_bytes,
        is_encrypted=storage.is_encrypted,
        created_at=storage.created_at,
        updated_at=storage.updated_at,
    )
