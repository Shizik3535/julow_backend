from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import RichTextSchema


class UpdateProjectMilestoneRequest(BaseModel):
    """Запрос на обновление milestone проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=1, max_length=200, description="Название milestone")
    due_date: str | None = Field(None, description="Дедлайн milestone (ISO date)")
    description: RichTextSchema | None = Field(None, description="Описание milestone")
