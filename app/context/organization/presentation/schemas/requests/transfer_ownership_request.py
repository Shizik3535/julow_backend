from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TransferOwnershipRequest(BaseModel):
    """
    Тело запроса передачи владения организацией.

    Атрибуты:
        from_id: UUID текущего владельца.
        to_id: UUID нового владельца.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_id": "550e8400-e29b-41d4-a716-446655440000",
                "to_id": "660e8400-e29b-41d4-a716-446655440001",
            },
        },
    )

    from_id: str = Field(
        ...,
        description="UUID текущего владельца",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    to_id: str = Field(
        ...,
        description="UUID нового владельца",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
