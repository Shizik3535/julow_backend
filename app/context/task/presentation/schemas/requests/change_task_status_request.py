from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeTaskStatusRequest(BaseModel):
    """Запрос на смену workflow-статуса задачи."""

    model_config = ConfigDict(from_attributes=True)

    new_status_id: str = Field(
        ...,
        description="UUID нового workflow-статуса",
        examples=["status-uuid"],
    )
