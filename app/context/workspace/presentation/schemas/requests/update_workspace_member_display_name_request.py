from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceMemberDisplayNameRequest(BaseModel):
    """
    Запрос на обновление отображаемого имени участника workspace.

    Атрибуты:
        display_name: Новое отображаемое имя.
    """

    model_config = ConfigDict(from_attributes=True)

    display_name: str = Field(..., min_length=1, max_length=200, description="Новое отображаемое имя")
