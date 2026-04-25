from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectRoleRequest(BaseModel):
    """Запрос на создание кастомной роли проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название роли")
    permissions: list[str] = Field(..., description="Список прав роли")
    description: str | None = Field(None, description="Описание роли")
