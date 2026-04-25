from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateProjectRoleRequest(BaseModel):
    """Запрос на обновление роли проекта."""

    model_config = ConfigDict(from_attributes=True)

    permissions: list[str] | None = Field(None, description="Новые разрешения роли")
    description: str | None = Field(None, description="Описание роли")
