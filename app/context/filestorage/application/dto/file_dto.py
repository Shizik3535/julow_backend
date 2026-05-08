from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class FileVersionDTO(BaseDTO):
    """DTO версии файла."""

    version_number: int
    storage_path: str
    size_bytes: int
    uploader_id: str
    change_summary: str | None = None
    uploaded_at: datetime | None = None


class FilePermissionEntryDTO(BaseDTO):
    """DTO разрешения на файл/папку."""

    id: str
    user_id: str | None = None
    team_id: str | None = None
    access_level: str
    granted_by: str
    granted_at: datetime | None = None


class PublicShareLinkDTO(BaseDTO):
    """DTO публичной ссылки на файл."""

    id: str
    token: str
    has_password: bool = False
    expires_at: datetime | None = None
    access_level: str
    allow_download: bool = True
    max_uses: int | None = None
    current_uses: int = 0
    created_by: str
    created_at: datetime | None = None


class FileTagDTO(BaseDTO):
    """DTO тега файла."""

    id: str
    name: str
    color: str | None = None


class FileLockDTO(BaseDTO):
    """DTO блокировки файла."""

    locked_by: str
    locked_at: datetime | None = None
    expires_at: datetime | None = None
    reason: str | None = None


class FileDTO(BaseDTO):
    """DTO файла."""

    id: str
    name: str
    original_name: str
    file_type: str
    size_bytes: int
    mime_type: str
    storage_id: str
    storage_path: str
    folder_id: str | None = None
    uploader_id: str
    workspace_id: str
    owner_id: str
    description: str | None = None
    scan_status: str
    status: str
    permissions: list[FilePermissionEntryDTO] = []
    versions: list[FileVersionDTO] = []
    lock: FileLockDTO | None = None
    tags: list[FileTagDTO] = []
    share_links: list[PublicShareLinkDTO] = []
    preview_path: str | None = None
    is_shared: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FileListDTO(BaseDTO):
    """Список файлов с пагинацией."""

    items: list[FileDTO] = []
    total: int = 0
