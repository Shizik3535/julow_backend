from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class UpdateSprintDateRangeRequest(BaseModel):
    """Запрос на обновление диапазона дат спринта."""

    model_config = ConfigDict(from_attributes=True)

    start_date: date | None = Field(None, description="Дата начала")
    end_date: date | None = Field(None, description="Дата окончания")
