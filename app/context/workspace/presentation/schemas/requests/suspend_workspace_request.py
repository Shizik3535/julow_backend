from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SuspendWorkspaceRequest(BaseModel):
    """
    Запрос на приостановку workspace.

    Атрибуты:
        reason: Причина приостановки.
    """

    model_config = ConfigDict(from_attributes=True)

    reason: str = Field(..., min_length=1, max_length=500, description="Причина приостановки")
