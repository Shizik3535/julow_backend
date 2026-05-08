from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO

from app.context.filestorage.application.dto.file_dto import FilePermissionEntryDTO


class FolderDTO(BaseDTO):
    """DTO папки."""

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
    permissions: list[FilePermissionEntryDTO] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FolderListDTO(BaseDTO):
    """Список папок."""

    items: list[FolderDTO] = []
    total: int = 0
