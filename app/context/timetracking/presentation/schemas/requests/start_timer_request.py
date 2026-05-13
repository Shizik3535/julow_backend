from __future__ import annotations

from pydantic import BaseModel, Field


class StartTimerRequest(BaseModel):
    """Тело запроса POST /timer/start."""

    workspace_id: str = Field(..., description="ID workspace")
    task_id: str | None = Field(default=None, description="ID задачи (опционально)")
    project_id: str | None = Field(default=None, description="ID проекта (опционально)")
    epic_id: str | None = Field(default=None, description="ID эпика (опционально)")
    description: str | None = Field(default=None, description="Описание")
