from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectVisibilityRequest(BaseModel):
    """Запрос на изменение видимости проекта."""

    model_config = ConfigDict(from_attributes=True)

    visibility: Literal["private", "workspace", "organization", "public"] = Field(
        ..., description="Видимость: private | workspace | organization | public", examples=["workspace"]
    )
