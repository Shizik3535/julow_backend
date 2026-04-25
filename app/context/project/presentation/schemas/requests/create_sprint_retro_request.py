from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateSprintRetroRequest(BaseModel):
    """Запрос на создание ретроспективы спринта."""

    model_config = ConfigDict(from_attributes=True)

    template_id: str = Field(..., description="UUID шаблона ретроспективы")
