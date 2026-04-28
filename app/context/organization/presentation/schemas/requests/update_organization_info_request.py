from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateOrganizationInfoRequest(BaseModel):
    """
    Тело запроса обновления информации организации.

    Атрибуты:
        name: Новое название (None — без изменений).
        personalization_color: Акцентный цвет (#RRGGBB).
        personalization_icon: Название иконки.
        personalization_display_name: Отображаемое имя.
        personalization_custom_domain: Кастомный домен.
        branding_logo_url: URL логотипа.
        branding_favicon_url: URL фавикона.
        branding_custom_css: Пользовательский CSS.
        branding_login_message: Сообщение на странице входа.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acme Corp Updated",
                "personalization_color": "#3366FF",
                "personalization_display_name": "Acme",
            },
        },
    )

    name: str | None = Field(default=None, min_length=1, max_length=255, description="Новое название")
    personalization_color: str | None = Field(default=None, max_length=7, description="Акцентный цвет (#RRGGBB)", examples=["#3366FF"])
    personalization_icon: str | None = Field(default=None, max_length=255, description="Название иконки")
    personalization_display_name: str | None = Field(default=None, max_length=255, description="Отображаемое имя")
    personalization_custom_domain: str | None = Field(default=None, max_length=255, description="Кастомный домен")
    branding_logo_url: str | None = Field(default=None, max_length=2048, description="URL логотипа")
    branding_favicon_url: str | None = Field(default=None, max_length=2048, description="URL фавикона")
    branding_custom_css: str | None = Field(default=None, max_length=10000, description="Пользовательский CSS")
    branding_login_message: str | None = Field(default=None, max_length=1000, description="Сообщение на странице входа")
