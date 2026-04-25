from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SendWorkspaceInvitationRequest(BaseModel):
    """
    Запрос на отправку email-приглашения в workspace.

    Атрибуты:
        email: Email приглашаемого.
        role_id: ID роли.
    """

    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="Email приглашаемого", examples=["user@example.com"])
    role_id: str = Field(..., description="UUID роли", examples=["role-uuid"])
