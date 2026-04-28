from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DigestSettingsResponse(BaseModel):
    """Ответ с настройками дайджеста уведомлений."""

    model_config = ConfigDict(from_attributes=True)

    enabled: bool = Field(default=False, description="Включён ли дайджест")
    frequency: str = Field(default="daily", description="Частота (daily/weekly)", examples=["daily"])
    delivery_time: str = Field(default="09:00", description="Время отправки (HH:MM)", examples=["09:00"])
    delivery_day: int | None = Field(default=None, description="День отправки для weekly (0=Пн, 6=Вс)", examples=[0])
    timezone: str = Field(default="UTC", description="Часовой пояс", examples=["UTC"])
