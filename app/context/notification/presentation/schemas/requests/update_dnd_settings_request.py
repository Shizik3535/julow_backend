from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateDndSettingsRequest(BaseModel):
    """
    Тело запроса обновления расписания «Не беспокоить».

    Атрибуты:
        enabled: Включён ли DND.
        schedule_start: Начало расписания (HH:MM).
        schedule_end: Конец расписания (HH:MM).
        schedule_days: Дни недели (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "schedule_start": "22:00",
                "schedule_end": "08:00",
                "schedule_days": [0, 1, 2, 3, 4],
                "timezone": "Europe/Moscow",
            },
        },
    )

    enabled: bool = Field(
        default=False,
        description="Включён ли режим DND",
    )
    schedule_start: str | None = Field(
        default=None,
        max_length=5,
        description="Начало расписания (HH:MM)",
        examples=["22:00"],
    )
    schedule_end: str | None = Field(
        default=None,
        max_length=5,
        description="Конец расписания (HH:MM)",
        examples=["08:00"],
    )
    schedule_days: list[int] | None = Field(
        default=None,
        description="Дни недели (0=Пн, 6=Вс). None = каждый день",
        examples=[[0, 1, 2, 3, 4]],
    )
    timezone: str = Field(
        default="UTC",
        max_length=50,
        description="Часовой пояс",
        examples=["UTC", "Europe/Moscow"],
    )
