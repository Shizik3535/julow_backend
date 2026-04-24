from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddTrustedDeviceRequest(BaseModel):
    """
    Тело запроса добавления доверенного устройства.

    Атрибуты:
        device_fingerprint: Отпечаток устройства.
        expires_at: Время истечения доверия (ISO 8601, опционально).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "device_fingerprint": "abc123def456",
                "expires_at": "2026-07-01T00:00:00Z",
            },
        },
    )

    device_fingerprint: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Уникальный отпечаток устройства",
        examples=["abc123def456"],
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Время истечения доверия (ISO 8601, опционально)",
        examples=["2026-07-01T00:00:00Z"],
    )
