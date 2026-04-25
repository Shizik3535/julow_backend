from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CreateSprintRequest(BaseModel):
    """Запрос на создание спринта."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200, description="Название спринта")
    goal: str | None = Field(None, description="Цель спринта")
    start_date: date | None = Field(None, description="Дата начала")
    end_date: date | None = Field(None, description="Дата окончания")
