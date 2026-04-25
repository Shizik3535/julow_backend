from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateOrgMemberDisplayNameRequest(BaseModel):
    """
    Тело запроса обновления отображаемого имени участника.

    Атрибуты:
        display_name: Новое отображаемое имя.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "display_name": "Пётр Сидоров",
            },
        },
    )

    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Новое отображаемое имя",
        examples=["Пётр Сидоров"],
    )
