from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GenerateProjectInvitationLinkRequest(BaseModel):
    """
    Запрос на генерацию ссылки/кода приглашения в проект.

    Атрибуты:
        role_id: ID роли проекта.
        expires_at: Время истечения ссылки.
        max_uses: Макс. количество использований. По умолчанию `1` — ссылка
            одноразовая. UI не показывает это поле, чтобы не путать пользователя.
    """

    model_config = ConfigDict(from_attributes=True)

    role_id: str = Field(..., description="UUID роли проекта", examples=["role-uuid"])
    expires_at: datetime | None = Field(default=None, description="Время истечения (UTC)")
    max_uses: int | None = Field(default=1, description="Макс. использований (по умолчанию 1)")
