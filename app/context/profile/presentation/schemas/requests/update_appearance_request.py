from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateAppearanceRequest(BaseModel):
    """
    Тело запроса обновления настроек внешнего вида.

    Атрибуты:
        theme: Тема оформления (light, dark, system, custom).
        accent_color: Акцентный цвет в формате #RRGGBB.
        interface_density: Плотность интерфейса (compact, comfortable, spacious).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "theme": "dark",
                "accent_color": "#6366F1",
                "interface_density": "comfortable",
            },
        },
    )

    theme: str = Field(
        default="system",
        description="Тема оформления (light, dark, system, custom)",
        examples=["dark"],
    )
    accent_color: str = Field(
        default="#6366F1",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Акцентный цвет в формате #RRGGBB",
        examples=["#6366F1"],
    )
    interface_density: str = Field(
        default="comfortable",
        description="Плотность интерфейса (compact, comfortable, spacious)",
        examples=["comfortable"],
    )
