from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateOrgRoleRequest(BaseModel):
    """
    Тело запроса обновления роли организации.

    Атрибуты:
        permissions: Новый список разрешений.
        description: Новое описание.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "permissions": ["projects.read", "projects.write", "members.read", "members.write"],
                "description": "Менеджер проектов (обновлено)",
            },
        },
    )

    permissions: list[str] | None = Field(
        default=None,
        description="Новый список разрешений",
        examples=[["projects.read", "projects.write", "members.read", "members.write"]],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Новое описание",
        examples=["Менеджер проектов (обновлено)"],
    )
