from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SuspendOrganizationRequest(BaseModel):
    """
    Тело запроса приостановки организации.

    Атрибуты:
        reason: Причина приостановки.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reason": "Нарушение условий использования",
            },
        },
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Причина приостановки",
        examples=["Нарушение условий использования"],
    )
