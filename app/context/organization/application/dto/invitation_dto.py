from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class InvitationDTO(BaseDTO):
    """
    DTO приглашения (Organization BC).

    Атрибуты:
        id: Идентификатор приглашения.
        org_id: ID организации.
        email: Email для email-приглашений.
        link: Данные токена для link-приглашений.
        role_id: ID роли.
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус приглашения.
        approved_by: ID подтвердившего.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str
    email: str | None = None
    link: dict[str, Any] | None = None
    role_id: str = ""
    invited_by: str = ""
    invited_at: datetime
    status: str = "PENDING"
    approved_by: str | None = None
    created_at: datetime
    updated_at: datetime


class InvitationListDTO(BaseDTO):
    """Список приглашений с общим количеством."""

    items: list[InvitationDTO]
    total: int
