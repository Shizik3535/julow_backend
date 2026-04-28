from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DndSettingsResponse(BaseModel):
    """Ответ с настройками режима «Не беспокоить»."""

    model_config = ConfigDict(from_attributes=True)

    enabled: bool = Field(default=False, description="Включён ли DND")
    schedule_start: str | None = Field(default=None, description="Начало расписания (HH:MM)", examples=["22:00"])
    schedule_end: str | None = Field(default=None, description="Конец расписания (HH:MM)", examples=["08:00"])
    schedule_days: list[int] | None = Field(default=None, description="Дни недели (0=Пн, 6=Вс)", examples=[[0, 1, 2, 3, 4]])
    timezone: str = Field(default="UTC", description="Часовой пояс", examples=["UTC"])
