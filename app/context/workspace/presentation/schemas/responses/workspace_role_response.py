from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceRoleResponse(BaseModel):
    """
    Ответ с данными роли workspace.

    Атрибуты:
        id: Идентификатор роли.
        workspace_id: ID workspace (пустая строка для системных).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID роли",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    workspace_id: str = Field(
        ...,
        description="UUID workspace (пустая строка для системных)",
        examples=["ws-uuid"],
    )
    name: str = Field(..., description="Название роли", examples=["admin"])
    permissions: list[str] = Field(..., description="Список разрешений", examples=[["members.write", "teams.write"]])
    is_system: bool = Field(..., description="Является ли роль системной")
    description: str | None = Field(
        default=None,
        description="Описание роли",
        examples=["Workspace administrator"],
    )
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
