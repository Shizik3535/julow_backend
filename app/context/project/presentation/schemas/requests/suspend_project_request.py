from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SuspendProjectRequest(BaseModel):
    """Запрос на приостановку проекта."""

    model_config = ConfigDict(from_attributes=True)

    reason: str = Field(..., min_length=1, max_length=1000, description="Причина приостановки")
