from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceSettingsResponse(BaseModel):
    """
    Ответ с настройками workspace (политики + лимиты).

    Атрибуты:
        workspace_id: ID workspace.
        security_policy: Политика безопасности (dict).
        membership_policy: Политика членства (dict).
        limits: Лимиты workspace (dict).
    """

    model_config = ConfigDict(from_attributes=True)

    workspace_id: str = Field(
        ...,
        description="UUID workspace",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    security_policy: dict[str, Any] = Field(..., description="Политика безопасности")
    membership_policy: dict[str, Any] = Field(..., description="Политика членства")
    limits: dict[str, Any] = Field(..., description="Лимиты workspace")
