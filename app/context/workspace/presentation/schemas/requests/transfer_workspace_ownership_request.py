from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TransferWorkspaceOwnershipRequest(BaseModel):
    """
    Запрос на передачу владения workspace.

    Атрибуты:
        from_id: ID текущего владельца.
        to_id: ID нового владельца.
    """

    model_config = ConfigDict(from_attributes=True)

    from_id: str = Field(..., description="UUID текущего владельца", examples=["user-uuid-from"])
    to_id: str = Field(..., description="UUID нового владельца", examples=["user-uuid-to"])
