from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateTeamRequest(BaseModel):
    """
    Тело запроса обновления команды.

    Атрибуты:
        name: Новое название.
        description: Новое описание.
        lead_id: Новый UUID лидера.
        icon: Название иконки.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Backend Team Updated",
                "description": "Обновлённое описание",
                "lead_id": "770e8400-e29b-41d4-a716-446655440002",
                "icon": "Code",
            },
        },
    )

    name: str | None = Field(default=None, min_length=1, max_length=255, description="Новое название")
    description: str | None = Field(default=None, max_length=1000, description="Новое описание")
    lead_id: str | None = Field(default=None, description="Новый UUID лидера")
    icon: str | None = Field(default=None, max_length=255, description="Новое название иконки")
