from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvitationResponse(BaseModel):
    """
    Ответ с данными приглашения.

    Атрибуты:
        id: UUID приглашения.
        org_id: UUID организации.
        email: Email для email-приглашений.
        link: Данные токена для link-приглашений.
        role_id: UUID роли.
        invited_by: UUID пригласившего.
        invited_at: Время приглашения.
        status: Статус приглашения.
        approved_by: UUID подтвердившего.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID приглашения",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        ...,
        description="UUID организации",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
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
        default="",
        description="UUID роли",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    invited_by: str = Field(
        default="",
        description="UUID пригласившего",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )
    invited_at: datetime = Field(..., description="Время приглашения (UTC)")
    status: str = Field(
        default="PENDING",
        description="Статус приглашения",
        examples=["PENDING"],
    )
    approved_by: str | None = Field(
        default=None,
        description="UUID подтвердившего",
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
