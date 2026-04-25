from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import DateRangeSchema


class SprintResponse(BaseModel):
    """Ответ с данными спринта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID спринта")
    project_id: str = Field(..., description="UUID проекта")
    name: str = Field(..., description="Название спринта")
    goal: str | None = Field(None, description="Цель спринта")
    status: str = Field(..., description="Статус: planning | active | completed | cancelled")
    date_range: DateRangeSchema | None = Field(None, description="Диапазон дат спринта")
    retro: dict[str, Any] | None = Field(None, description="Данные ретроспективы")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
