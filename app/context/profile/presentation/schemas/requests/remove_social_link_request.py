from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RemoveSocialLinkRequest(BaseModel):
    """
    Тело запроса удаления социальной ссылки.

    Атрибуты:
        platform: Название платформы для удаления.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "platform": "github",
            },
        },
    )

    platform: str = Field(
        ...,
        max_length=50,
        description="Название платформы для удаления",
        examples=["github"],
    )
