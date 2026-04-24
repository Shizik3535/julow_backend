from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UnpinItemRequest(BaseModel):
    """
    Тело запроса открепления элемента.

    Атрибуты:
        target_type: Тип элемента (WORKSPACE, PROJECT, TASK, DASHBOARD, REPORT).
        target_id: ID элемента.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_type": "PROJECT",
                "target_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        },
    )

    target_type: str = Field(
        ...,
        description="Тип элемента (WORKSPACE, PROJECT, TASK, DASHBOARD, REPORT)",
        examples=["PROJECT"],
    )
    target_id: str = Field(
        ...,
        description="ID элемента",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
