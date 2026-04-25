from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceInvitationResponse(BaseModel):
    """
    Ответ с данными приглашения в workspace.

    Атрибуты:
        id: Идентификатор приглашения.
        workspace_id: ID workspace.
        email: Email (для email-приглашений).
        link: Данные токена ссылки (dict) или None.
        role_id: ID роли.
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус (PENDING, ACCEPTED, DECLINED, EXPIRED, REVOKED).
        approved_by: ID подтвердившего.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID приглашения",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    workspace_id: str = Field(
        ...,
        description="UUID workspace",
        examples=["ws-uuid"],
    )
    email: str | None = Field(
        default=None,
        description="Email приглашаемого",
        examples=["user@example.com"],
    )
    link: dict[str, Any] | None = Field(
        default=None,
        description="Данные ссылки-приглашения",
    )
    role_id: str = Field(
        ...,
        description="UUID роли",
        examples=["role-uuid"],
    )
    invited_by: str = Field(
        ...,
        description="UUID пригласившего",
        examples=["inviter-uuid"],
    )
    invited_at: datetime = Field(..., description="Время приглашения (UTC)")
    status: str = Field(
        ...,
        description="Статус приглашения",
        examples=["PENDING"],
    )
    approved_by: str | None = Field(
        default=None,
        description="UUID подтвердившего",
        examples=["approver-uuid"],
    )
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
