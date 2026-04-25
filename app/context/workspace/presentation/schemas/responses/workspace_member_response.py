from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceMemberResponse(BaseModel):
    """
    Ответ с данными участника workspace.

    Атрибуты:
        id: Идентификатор записи участника.
        user_id: ID пользователя.
        display_name: Отображаемое имя в рамках workspace.
        role_id: ID роли.
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        source: Источник (DIRECT, ORGANIZATION, PARENT_WORKSPACE, INVITATION_LINK).
        invited_by: ID пригласившего.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID записи участника",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: str = Field(
        ...,
        description="UUID пользователя",
        examples=["user-uuid"],
    )
    display_name: str | None = Field(
        default=None,
        description="Отображаемое имя в рамках workspace",
        examples=["John Doe"],
    )
    role_id: str = Field(
        ...,
        description="UUID роли",
        examples=["role-uuid"],
    )
    joined_at: datetime = Field(..., description="Время присоединения (UTC)")
    is_active: bool = Field(..., description="Активен ли участник")
    source: str = Field(
        ...,
        description="Источник добавления",
        examples=["DIRECT"],
    )
    invited_by: str | None = Field(
        default=None,
        description="UUID пригласившего",
        examples=["inviter-uuid"],
    )
