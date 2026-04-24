from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    """
    Ответ с данными пользователя.

    Содержит публичную информацию о пользователе,
    безопасную для передачи клиенту.

    Атрибуты:
        id: UUID пользователя.
        email: Email-адрес.
        status: Текущий статус аккаунта (active, pending_verification, locked и т.д.).
        role_ids: Список UUID ролей пользователя.
        is_email_confirmed: Подтверждён ли email-адрес.
        created_at: Дата и время регистрации (UTC).
        updated_at: Дата и время последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID пользователя", examples=["550e8400-e29b-41d4-a716-446655440000"])
    email: str = Field(..., description="Email-адрес", examples=["user@example.com"])
    status: str = Field(..., description="Статус аккаунта", examples=["active"])
    role_ids: list[str] = Field(default_factory=list, description="Список UUID ролей")
    is_email_confirmed: bool = Field(..., description="Подтверждён ли email")
    created_at: datetime = Field(..., description="Дата регистрации (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
