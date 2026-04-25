from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GenerateWorkspaceInvitationLinkRequest(BaseModel):
    """
    Запрос на генерацию ссылки-приглашения в workspace.

    Атрибуты:
        role_id: ID роли.
        expires_at: Время истечения ссылки.
        max_uses: Макс. количество использований.
    """

    model_config = ConfigDict(from_attributes=True)

    role_id: str = Field(..., description="UUID роли", examples=["role-uuid"])
    expires_at: datetime | None = Field(default=None, description="Время истечения ссылки (UTC)")
    max_uses: int | None = Field(default=None, description="Макс. количество использований")
