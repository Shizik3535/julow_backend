from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssignTaskToEpicRequest(BaseModel):
    """Запрос на привязку задачи к эпику."""

    model_config = ConfigDict(from_attributes=True)

    epic_id: str = Field(
        ...,
        description="UUID эпика",
        examples=["epic-uuid"],
    )
