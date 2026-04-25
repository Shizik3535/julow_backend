from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssignTaskToSprintRequest(BaseModel):
    """Запрос на привязку задачи к спринту."""

    model_config = ConfigDict(from_attributes=True)

    sprint_id: str = Field(
        ...,
        description="UUID спринта",
        examples=["sprint-uuid"],
    )
