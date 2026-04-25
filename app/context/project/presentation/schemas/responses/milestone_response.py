from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import RichTextSchema


class MilestoneResponse(BaseModel):
    """Ответ с данными milestone проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID milestone")
    name: str = Field(..., description="Название milestone")
    description: RichTextSchema | None = Field(None, description="Описание")
    status: str = Field(..., description="Статус: not_started | in_progress | completed | overdue")
    due_date: str | None = Field(None, description="Дата дедлайна")
    completed_at: datetime | None = Field(None, description="Дата завершения (UTC)")
