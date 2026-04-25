from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SendBulkWorkspaceInvitationsRequest(BaseModel):
    """
    Запрос на массовую отправку email-приглашений в workspace.

    Атрибуты:
        emails: Список email-адресов.
        role_id: ID роли для всех приглашённых.
    """

    model_config = ConfigDict(from_attributes=True)

    emails: list[str] = Field(..., min_length=1, description="Список email-адресов")
    role_id: str = Field(..., description="UUID роли", examples=["role-uuid"])
