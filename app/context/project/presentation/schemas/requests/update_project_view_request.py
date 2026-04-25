from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateProjectViewRequest(BaseModel):
    """Запрос на обновление представления проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=1, max_length=100, description="Название представления")
    view_type: str | None = Field(None, description="Тип: board | list | timeline | calendar | table")
