from __future__ import annotations

from pydantic import BaseModel


class UpdateTimeEntryRequest(BaseModel):
    """Тело PATCH /time-entries/{entry_id}."""

    description: str | None = None
    is_billable: bool | None = None
    hourly_rate_amount: str | None = None
    hourly_rate_currency: str | None = None
    category_id: str | None = None
