from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateDepartmentRequest(BaseModel):
    """
    Тело запроса создания подразделения.

    Атрибуты:
        name: Название подразделения.
        parent_id: UUID родительского подразделения.
        lead_id: UUID руководителя.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Engineering",
                "parent_id": None,
                "lead_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        },
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название подразделения",
        examples=["Engineering"],
    )
    parent_id: str | None = Field(
        default=None,
        description="UUID родительского подразделения",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    lead_id: str | None = Field(
        default=None,
        description="UUID руководителя",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
