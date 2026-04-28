from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceInfoRequest(BaseModel):
    """
    Запрос на обновление информации workspace.

    Атрибуты:
        name: Новое название.
        color: Основной цвет (HEX).
        icon: Название иконки.
        display_name: Отображаемое имя.
        description: Описание.
        cover_image_url: URL обложки.
        custom_css: Пользовательский CSS.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, min_length=3, max_length=100, description="Название workspace")
    color: str | None = Field(default=None, description="Основной цвет (HEX)", examples=["#FF5500"])
    icon: str | None = Field(default=None, description="Название иконки")
    display_name: str | None = Field(default=None, description="Отображаемое имя")
    description: str | None = Field(default=None, max_length=500, description="Описание")
    cover_image_url: str | None = Field(default=None, description="URL обложки")
    custom_css: str | None = Field(default=None, description="Пользовательский CSS")
