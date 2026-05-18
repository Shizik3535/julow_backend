from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SendProjectInvitationRequest(BaseModel):
    """
    Запрос на отправку email-приглашения в проект.

    Атрибуты:
        email: Email приглашаемого.
        role_id: ID роли проекта.
    """

    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="Email приглашаемого", examples=["user@example.com"])
    role_id: str = Field(..., description="UUID роли проекта", examples=["role-uuid"])
