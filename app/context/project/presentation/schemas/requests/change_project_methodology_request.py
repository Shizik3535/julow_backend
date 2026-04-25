from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectMethodologyRequest(BaseModel):
    """Запрос на смену методологии проекта."""

    model_config = ConfigDict(from_attributes=True)

    new_methodology: str = Field(
        ..., description="Новая методология: kanban | scrum | waterfall | hybrid | shape_up", examples=["scrum"]
    )
