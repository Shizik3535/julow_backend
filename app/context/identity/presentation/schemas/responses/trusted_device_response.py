from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TrustedDeviceResponse(BaseModel):
    """
    Ответ с данными доверенного устройства.

    Атрибуты:
        device_fingerprint: Отпечаток устройства.
        user_agent: User-Agent устройства.
        ip: IP-адрес.
        trusted_at: Время добавления в доверенные (UTC).
        expires_at: Время истечения доверия (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    device_fingerprint: str = Field(..., description="Отпечаток устройства", examples=["abc123def456"])
    user_agent: str = Field(..., description="User-Agent устройства", examples=["Mozilla/5.0 ..."])
    ip: str = Field(..., description="IP-адрес", examples=["192.168.1.1"])
    trusted_at: datetime | None = Field(default=None, description="Время добавления (UTC)")
    expires_at: datetime | None = Field(default=None, description="Время истечения доверия (UTC)")
