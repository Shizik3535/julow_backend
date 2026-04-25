from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SendInvitationRequest(BaseModel):
    """
    Тело запроса отправки email-приглашения.

    Атрибуты:
        email: Email приглашаемого.
        role_id: UUID роли.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "role_id": "770e8400-e29b-41d4-a716-446655440002",
            },
        },
    )

    email: str = Field(
        ...,
        description="Email приглашаемого",
        examples=["user@example.com"],
    )
    role_id: str = Field(
        ...,
        description="UUID роли",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
