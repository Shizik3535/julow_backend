from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateDepartmentRequest(BaseModel):
    """
    Тело запроса обновления подразделения.

    Атрибуты:
        name: Новое название.
        lead_id: Новый UUID руководителя.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Engineering Updated",
                "lead_id": "770e8400-e29b-41d4-a716-446655440002",
            },
        },
    )

    name: str | None = Field(default=None, min_length=1, max_length=255, description="Новое название")
    lead_id: str | None = Field(default=None, description="Новый UUID руководителя")
