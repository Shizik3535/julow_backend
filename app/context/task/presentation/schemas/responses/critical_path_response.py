from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CriticalPathNodeResponse(BaseModel):
    """Узел критического пути."""

    model_config = ConfigDict(from_attributes=True)

    task_id: str
    title: str
    start_date: str | None = None
    due_date: str | None = None
    duration_days: int = 0
    slack_days: float = 0.0


class CriticalPathResponse(BaseModel):
    """Результат расчёта критического пути проекта."""

    model_config = ConfigDict(from_attributes=True)

    path: list[CriticalPathNodeResponse] = Field(default_factory=list)
    total_duration_days: int = 0
