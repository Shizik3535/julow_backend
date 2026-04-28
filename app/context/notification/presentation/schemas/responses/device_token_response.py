from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceTokenResponse(BaseModel):
    """Ответ с данными токена устройства."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID токена устройства", examples=["550e8400-e29b-41d4-a716-446655440000"])
    platform: str = Field(..., description="Платформа (ios/android/web)", examples=["android"])
    device_name: str = Field(default="", description="Название устройства", examples=["Samsung Galaxy S24"])
    is_active: bool = Field(default=True, description="Активен ли токен")
    last_used_at: datetime | None = Field(default=None, description="Время последнего использования (UTC)")
