from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SendBulkInvitationsRequest(BaseModel):
    """
    Тело запроса массовой отправки email-приглашений.

    Атрибуты:
        emails: Список email-адресов.
        role_id: UUID роли для всех приглашений.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "emails": ["user1@example.com", "user2@example.com"],
                "role_id": "770e8400-e29b-41d4-a716-446655440002",
            },
        },
    )

    emails: list[str] = Field(
        ...,
        min_length=1,
        description="Список email-адресов",
        examples=[["user1@example.com", "user2@example.com"]],
    )
    role_id: str = Field(
        ...,
        description="UUID роли для всех приглашений",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
