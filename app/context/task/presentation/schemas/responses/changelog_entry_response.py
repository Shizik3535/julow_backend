from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChangelogEntryResponse(BaseModel):
    """Ответ с записью истории изменений задачи."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str = Field(..., description="ID задачи")
    field_name: str = Field(..., description="Имя изменённого поля")
    old_value: str | None = Field(default=None, description="Старое значение")
    new_value: str | None = Field(default=None, description="Новое значение")
    changed_by: str = Field(..., description="ID изменившего")
    changed_at: datetime | str = Field(..., description="Дата/время изменения")
