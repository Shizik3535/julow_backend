from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectRoleResponse(BaseModel):
    """Ответ с данными роли проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID роли")
    project_id: str = Field(..., description="UUID проекта")
    name: str = Field(..., description="Название роли", examples=["admin"])
    permissions: list[str] = Field(default_factory=list, description="Список прав роли")
    is_system: bool = Field(..., description="Является ли системной ролью")
    description: str | None = Field(None, description="Описание роли")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
