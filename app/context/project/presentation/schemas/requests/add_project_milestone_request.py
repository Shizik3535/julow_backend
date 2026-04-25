from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import RichTextSchema


class AddProjectMilestoneRequest(BaseModel):
    """Запрос на добавление milestone в проект."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200, description="Название milestone")
    due_date: str = Field(..., description="Дедлайн milestone (ISO date)", examples=["2025-06-01"])
    description: RichTextSchema | None = Field(None, description="Описание milestone")
