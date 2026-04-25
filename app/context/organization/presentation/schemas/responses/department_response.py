from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentResponse(BaseModel):
    """
    Ответ с данными подразделения.

    Атрибуты:
        id: UUID подразделения.
        org_id: UUID организации.
        name: Название подразделения.
        parent_id: UUID родительского подразделения.
        lead_id: UUID руководителя.
        member_ids: Список UUID участников.
        is_active: Активно ли подразделение.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID подразделения",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        ...,
        description="UUID организации",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    name: str = Field(
        ...,
        description="Название подразделения",
        examples=["Engineering"],
    )
    parent_id: str | None = Field(
        default=None,
        description="UUID родительского подразделения",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    lead_id: str | None = Field(
        default=None,
        description="UUID руководителя",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )
    member_ids: list[str] = Field(
        default_factory=list,
        description="Список UUID участников",
    )
    is_active: bool = Field(default=True, description="Активно ли подразделение")
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
