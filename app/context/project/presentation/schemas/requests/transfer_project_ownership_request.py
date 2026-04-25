from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TransferProjectOwnershipRequest(BaseModel):
    """Запрос на передачу владения проектом."""

    model_config = ConfigDict(from_attributes=True)

    from_owner_id: str = Field(..., description="UUID текущего владельца")
    to_owner_id: str = Field(..., description="UUID нового владельца")
