from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddWorkspaceOwnerRequest(BaseModel):
    """
    Запрос на добавление со-владельца workspace.

    Атрибуты:
        user_id: ID нового со-владельца.
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID нового со-владельца", examples=["user-uuid"])
