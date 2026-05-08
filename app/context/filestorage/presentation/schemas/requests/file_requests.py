from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RenameFileRequest(BaseModel):
    """Тело запроса на переименование файла."""

    new_name: str = Field(..., min_length=1, max_length=512)


class MoveFileRequest(BaseModel):
    """Тело запроса на перемещение файла."""

    new_folder_id: str


class UpdateFileDescriptionRequest(BaseModel):
    """Тело запроса на обновление описания файла."""

    description: str | None = None


class GrantFilePermissionRequest(BaseModel):
    """Тело запроса на выдачу разрешения на файл."""

    user_id: str | None = None
    team_id: str | None = None
    access_level: str = "view"


class LockFileRequest(BaseModel):
    """Тело запроса на блокировку файла."""

    reason: str | None = None
    expires_at: datetime | None = None


class AddFileTagRequest(BaseModel):
    """Тело запроса на добавление тега."""

    tag_name: str = Field(..., min_length=1, max_length=64)
    color: str | None = None


class CreateShareLinkRequest(BaseModel):
    """Тело запроса на создание публичной ссылки."""

    access_level: str = "view"
    password: str | None = None
    expires_at: datetime | None = None
    max_uses: int | None = Field(default=None, ge=1)


class AccessShareLinkRequest(BaseModel):
    """Тело запроса перехода по публичной ссылке (для запроса с паролем)."""

    password: str | None = None
