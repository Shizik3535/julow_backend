from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateOrgRoleRequest(BaseModel):
    """
    Тело запроса создания кастомной роли.

    Атрибуты:
        name: Название роли.
        permissions: Список разрешений.
        scope: Область действия (ORG, DEPARTMENT, TEAM).
        description: Описание роли.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "project_manager",
                "permissions": ["projects.read", "projects.write", "members.read"],
                "scope": "ORG",
                "description": "Менеджер проектов",
            },
        },
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название роли",
        examples=["project_manager"],
    )
    permissions: list[str] = Field(
        ...,
        min_length=1,
        description="Список разрешений",
        examples=[["projects.read", "projects.write", "members.read"]],
    )
    scope: str = Field(
        default="ORG",
        max_length=20,
        description="Область действия роли (ORG, DEPARTMENT, TEAM)",
        examples=["ORG"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Описание роли",
        examples=["Менеджер проектов"],
    )
