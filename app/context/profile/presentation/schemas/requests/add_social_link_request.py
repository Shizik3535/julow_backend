from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddSocialLinkRequest(BaseModel):
    """
    Тело запроса добавления социальной ссылки.

    Атрибуты:
        platform: Название платформы (github, linkedin и т.д.).
        url: URL профиля на платформе.
        display_name: Отображаемое имя (опционально).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "platform": "github",
                "url": "https://github.com/johndoe",
                "display_name": "John Doe",
            },
        },
    )

    platform: str = Field(
        ...,
        max_length=50,
        description="Название платформы",
        examples=["github"],
    )
    url: str = Field(
        ...,
        description="URL профиля на платформе",
        examples=["https://github.com/johndoe"],
    )
    display_name: str | None = Field(
        default=None,
        max_length=100,
        description="Отображаемое имя",
        examples=["John Doe"],
    )
