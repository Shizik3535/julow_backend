from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetEffortEstimateRequest(BaseModel):
    """Запрос на установку оценки усилия."""

    model_config = ConfigDict(from_attributes=True)

    value: float = Field(
        ...,
        gt=0,
        description="Значение оценки",
        examples=[8.0],
    )
    unit: str = Field(
        ...,
        description="Единица измерения (HOURS, STORY_POINTS, DAYS, T_SHIRT)",
        examples=["HOURS"],
    )
