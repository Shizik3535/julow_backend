from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TerminateAllSessionsResponse(BaseModel):
    """
    Ответ на завершение всех сессий кроме текущей.

    Атрибуты:
        terminated_count: Количество завершённых сессий.
    """

    model_config = ConfigDict(from_attributes=True)

    terminated_count: int = Field(..., description="Количество завершённых сессий", examples=[3])
