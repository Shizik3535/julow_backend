from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.context.filestorage.presentation.schemas.responses.file_response import (
    FilePermissionResponse,
)


class FolderResponse(BaseModel):
    id: str
    name: str
    folder_type: str
    parent_folder_id: str | None = None
    color: str | None = None
    description: str | None = None
    icon: str | None = None
    owner_id: str
    workspace_id: str
    project_id: str | None = None
    is_pinned: bool = False
    is_shared: bool = False
    permissions: list[FilePermissionResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FolderListResponse(BaseModel):
    items: list[FolderResponse] = []
    total: int = 0
