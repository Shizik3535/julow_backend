from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetReminderWindowRequest(BaseModel):
    """
    Тело запроса установки окна напоминания о дедлайне.

    Атрибуты:
        hours: Окно напоминания в часах (1–168).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hours": 48,
            },
        },
    )

    hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Окно напоминания о дедлайне (в часах, от 1 до 168)",
        examples=[24, 48],
    )
