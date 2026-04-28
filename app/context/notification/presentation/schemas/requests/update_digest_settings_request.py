from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateDigestSettingsRequest(BaseModel):
    """
    Тело запроса обновления конфигурации дайджеста.

    Атрибуты:
        enabled: Включён ли дайджест.
        frequency: Частота (daily/weekly).
        delivery_time: Время отправки (HH:MM).
        delivery_day: День отправки для weekly (0=Пн, 6=Вс).
        timezone: Часовой пояс.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "frequency": "daily",
                "delivery_time": "09:00",
                "timezone": "UTC",
            },
        },
    )

    enabled: bool = Field(
        default=False,
        description="Включён ли дайджест",
    )
    frequency: str = Field(
        default="daily",
        max_length=10,
        description="Частота (daily/weekly)",
        examples=["daily", "weekly"],
    )
    delivery_time: str = Field(
        default="09:00",
        max_length=5,
        description="Время отправки (HH:MM)",
        examples=["09:00"],
    )
    delivery_day: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="День отправки для weekly (0=Пн, 6=Вс)",
        examples=[0],
    )
    timezone: str = Field(
        default="UTC",
        max_length=50,
        description="Часовой пояс",
        examples=["UTC"],
    )
