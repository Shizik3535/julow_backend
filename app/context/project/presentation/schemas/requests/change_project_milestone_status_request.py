from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectMilestoneStatusRequest(BaseModel):
    """Запрос на изменение статуса milestone проекта."""

    model_config = ConfigDict(from_attributes=True)

    new_status: str = Field(
        ..., description="Новый статус: not_started | in_progress | completed | overdue", examples=["in_progress"]
    )
