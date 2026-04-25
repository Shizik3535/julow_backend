from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddBoardSwimlaneRequest(BaseModel):
    """Запрос на добавление swimlane на доску."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название swimlane")
    group_by: str = Field(
        ..., description="Способ группировки: assignee | priority | label | epic | custom_field", examples=["assignee"]
    )
    group_value: str | None = Field(None, description="Значение группировки")
