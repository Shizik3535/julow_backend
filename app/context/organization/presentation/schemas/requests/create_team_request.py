from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateTeamRequest(BaseModel):
    """
    Тело запроса создания команды.

    Атрибуты:
        name: Название команды.
        description: Описание.
        lead_id: UUID лидера.
        icon_url: URL иконки.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Backend Team",
                "description": "Команда разработки бэкенда",
                "lead_id": "550e8400-e29b-41d4-a716-446655440000",
                "icon_url": None,
            },
        },
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название команды",
        examples=["Backend Team"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Описание команды",
        examples=["Команда разработки бэкенда"],
    )
    lead_id: str | None = Field(
        default=None,
        description="UUID лидера команды",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    icon_url: str | None = Field(
        default=None,
        max_length=2048,
        description="URL иконки",
    )
