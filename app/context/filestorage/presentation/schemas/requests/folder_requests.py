from __future__ import annotations

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    """Тело запроса на создание папки."""

    workspace_id: str
    name: str = Field(..., min_length=1, max_length=512)
    parent_folder_id: str | None = None
    color: str | None = None
    description: str | None = None
    icon: str | None = None


class RenameFolderRequest(BaseModel):
    """Тело запроса на переименование папки."""

    new_name: str = Field(..., min_length=1, max_length=512)


class MoveFolderRequest(BaseModel):
    """Тело запроса на перемещение папки."""

    new_parent_folder_id: str


class UpdateFolderDescriptionRequest(BaseModel):
    """Тело запроса на обновление описания папки."""

    description: str | None = None
