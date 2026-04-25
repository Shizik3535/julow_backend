from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectVisibilityRequest(BaseModel):
    """Запрос на изменение видимости проекта."""

    model_config = ConfigDict(from_attributes=True)

    visibility: str = Field(
        ..., description="Видимость: private | workspace | organization | public", examples=["workspace"]
    )
