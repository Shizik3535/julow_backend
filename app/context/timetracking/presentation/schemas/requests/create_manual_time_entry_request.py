from __future__ import annotations

from pydantic import BaseModel, Field


class CreateManualTimeEntryRequest(BaseModel):
    """Тело запроса POST /time-entries (ручной ввод)."""

    workspace_id: str = Field(..., description="ID workspace")
    duration_seconds: int = Field(..., gt=0, description="Длительность в секундах (>0)")
    entry_date: str = Field(..., description="Дата записи (ISO 8601)")
    task_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str | None = None
    is_billable: bool = False
    hourly_rate_amount: str | None = Field(default=None, description="Сумма (Decimal как строка)")
    hourly_rate_currency: str | None = Field(default=None, description="ISO 4217")
    category_id: str | None = None
