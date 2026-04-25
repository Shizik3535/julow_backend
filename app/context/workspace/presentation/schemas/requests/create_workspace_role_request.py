from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateWorkspaceRoleRequest(BaseModel):
    """
    Запрос на создание кастомной роли в workspace.

    Атрибуты:
        name: Название роли.
        permissions: Список разрешений.
        description: Описание роли.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название роли", examples=["custom-admin"])
    permissions: list[str] = Field(..., min_length=1, description="Список разрешений", examples=[["members.write"]])
    description: str | None = Field(default=None, max_length=500, description="Описание роли")
