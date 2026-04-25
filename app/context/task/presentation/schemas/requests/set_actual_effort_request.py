from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetActualEffortRequest(BaseModel):
    """Запрос на установку фактического усилия."""

    model_config = ConfigDict(from_attributes=True)

    value: float = Field(
        ...,
        gt=0,
        description="Фактическое значение усилия",
        examples=[6.5],
    )
    unit: str = Field(
        ...,
        description="Единица измерения (HOURS, STORY_POINTS, DAYS, T_SHIRT)",
        examples=["HOURS"],
    )
