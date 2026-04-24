from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RoleResponse(BaseModel):
    """
    Ответ с данными роли.

    Содержит информацию о роли пользователя в системе,
    включая список разрешений.

    Атрибуты:
        id: UUID роли.
        name: Название роли (уникальное).
        permissions: Список строковых идентификаторов разрешений.
        is_system: Является ли роль системной (нельзя удалить).
        description: Текстовое описание роли.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID роли", examples=["550e8400-e29b-41d4-a716-446655440000"])
    name: str = Field(..., description="Название роли", examples=["admin"])
    permissions: list[str] = Field(default_factory=list, description="Список разрешений", examples=[["users.read", "users.write"]])
    is_system: bool = Field(..., description="Системная роль (нельзя удалить)")
    description: str | None = Field(default=None, description="Описание роли", examples=["Администратор системы"])
