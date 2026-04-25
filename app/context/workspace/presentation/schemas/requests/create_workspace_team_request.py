from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateWorkspaceTeamRequest(BaseModel):
    """
    Запрос на создание команды в workspace.

    Атрибуты:
        name: Название команды.
        lead_id: ID лидера команды (опционально).
    """

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название команды", examples=["Backend Team"])
    lead_id: str | None = Field(default=None, description="UUID лидера команды", examples=["lead-uuid"])
