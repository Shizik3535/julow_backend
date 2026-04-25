from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddWorkflowTransitionRequest(BaseModel):
    """Запрос на добавление перехода workflow."""

    model_config = ConfigDict(from_attributes=True)

    from_status_id: str = Field(..., description="UUID исходного статуса")
    to_status_id: str = Field(..., description="UUID целевого статуса")
    name: str = Field(..., min_length=1, max_length=100, description="Название перехода")
    required_permission: str | None = Field(None, description="Требуемое право для перехода")
