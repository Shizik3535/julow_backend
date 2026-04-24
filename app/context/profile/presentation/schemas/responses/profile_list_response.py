from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.profile.presentation.schemas.responses.profile_response import ProfileResponse


class ProfileListResponse(BaseModel):
    """
    Ответ со списком профилей.

    Атрибуты:
        items: Список профилей.
        total: Общее количество записей.
    """

    model_config = ConfigDict(from_attributes=True)

    items: list[ProfileResponse] = Field(default_factory=list, description="Список профилей")
    total: int = Field(default=0, description="Общее количество записей")
