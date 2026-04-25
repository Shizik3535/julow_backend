from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddWorkspaceMemberRequest(BaseModel):
    """
    Запрос на добавление участника в workspace.

    Атрибуты:
        user_id: ID пользователя.
        role_id: ID роли.
        source: Источник добавления (DIRECT, ORGANIZATION, PARENT_WORKSPACE).
        display_name: Отображаемое имя.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID пользователя", examples=["user-uuid"])
    role_id: str = Field(..., description="UUID роли", examples=["role-uuid"])
    source: str | None = Field(default=None, description="Источник добавления", examples=["DIRECT"])
    display_name: str | None = Field(default=None, description="Отображаемое имя", examples=["John Doe"])
