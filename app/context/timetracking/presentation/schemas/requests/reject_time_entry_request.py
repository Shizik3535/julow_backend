from __future__ import annotations

from pydantic import BaseModel, Field


class RejectTimeEntryRequest(BaseModel):
    """Тело POST /time-entries/{entry_id}/reject."""

    reason: str = Field(..., min_length=1, description="Причина отклонения")
