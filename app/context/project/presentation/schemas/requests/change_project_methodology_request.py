from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectMethodologyRequest(BaseModel):
    """Запрос на смену методологии проекта."""

    model_config = ConfigDict(from_attributes=True)

    new_methodology: Literal["kanban", "scrum", "waterfall", "hybrid", "shape_up"] = Field(
        ..., description="Новая методология: kanban | scrum | waterfall | hybrid | shape_up", examples=["scrum"]
    )
