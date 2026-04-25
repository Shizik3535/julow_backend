from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceRoleRequest(BaseModel):
    """
    Запрос на обновление роли workspace.

    Атрибуты:
        permissions: Новый список разрешений.
        description: Новое описание.
    """

    model_config = ConfigDict(from_attributes=True)

    permissions: list[str] | None = Field(default=None, description="Новый список разрешений")
    description: str | None = Field(default=None, max_length=500, description="Новое описание роли")
