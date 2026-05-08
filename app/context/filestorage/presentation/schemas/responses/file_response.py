from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FileVersionResponse(BaseModel):
    version_number: int
    storage_path: str
    size_bytes: int
    uploader_id: str
    change_summary: str | None = None
    uploaded_at: datetime | None = None


class FilePermissionResponse(BaseModel):
    id: str
    user_id: str | None = None
    team_id: str | None = None
    access_level: str
    granted_by: str
    granted_at: datetime | None = None


class PublicShareLinkResponse(BaseModel):
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


class FileTagResponse(BaseModel):
    id: str
    name: str
    color: str | None = None


class FileLockResponse(BaseModel):
    locked_by: str
    locked_at: datetime | None = None
    expires_at: datetime | None = None
    reason: str | None = None


class FileResponse(BaseModel):
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
    permissions: list[FilePermissionResponse] = []
    versions: list[FileVersionResponse] = []
    lock: FileLockResponse | None = None
    tags: list[FileTagResponse] = []
    share_links: list[PublicShareLinkResponse] = []
    preview_path: str | None = None
    is_shared: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FileListResponse(BaseModel):
    items: list[FileResponse] = []
    total: int = 0


class FileDownloadUrlResponse(BaseModel):
    url: str
    expires_in: int
    file_id: str
    name: str
    mime_type: str
    size_bytes: int
