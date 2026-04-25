from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeOrgMemberRoleRequest(BaseModel):
    """
    Тело запроса изменения роли участника организации.

    Атрибуты:
        new_role_id: UUID новой роли.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_role_id": "770e8400-e29b-41d4-a716-446655440002",
            },
        },
    )

    new_role_id: str = Field(
        ...,
        description="UUID новой роли",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
