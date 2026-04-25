from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceLimitsRequest(BaseModel):
    """
    Запрос на обновление лимитов workspace.

    Атрибуты:
        max_projects: Макс. количество проектов.
        max_members: Макс. количество участников.
        max_storage_bytes: Макс. объём хранилища (байты).
        max_file_size_bytes: Макс. размер файла (байты).
        max_teams: Макс. количество команд.
    """

    model_config = ConfigDict(from_attributes=True)

    max_projects: int | None = Field(default=None, description="Макс. количество проектов")
    max_members: int | None = Field(default=None, description="Макс. количество участников")
    max_storage_bytes: int | None = Field(default=None, description="Макс. объём хранилища (байты)")
    max_file_size_bytes: int | None = Field(default=None, description="Макс. размер файла (байты)")
    max_teams: int | None = Field(default=None, description="Макс. количество команд")
