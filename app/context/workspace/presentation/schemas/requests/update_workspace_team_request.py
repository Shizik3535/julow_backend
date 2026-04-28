from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceTeamRequest(BaseModel):
    """
    Запрос на обновление команды workspace.

    Атрибуты:
        name: Новое название.
        description: Новое описание.
        lead_id: Новый ID лидера.
        icon: Новое название иконки.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, min_length=1, max_length=100, description="Название команды")
    description: str | None = Field(default=None, max_length=500, description="Описание команды")
    lead_id: str | None = Field(default=None, description="UUID лидера команды")
    icon: str | None = Field(default=None, description="Название иконки команды")
