from __future__ import annotations

from pydantic import BaseModel, Field


class QrLoginCreatedResponse(BaseModel):
    qr_token: str = Field(..., description="Одноразовый токен сессии QR")
    expires_at: str = Field(..., description="ISO-8601 время истечения")
    qr_uri: str = Field(..., description="Строка для кодирования в QR")
    poll_interval_ms: int = Field(default=2000, description="Рекомендуемый интервал опроса (мс)")


class QrLoginPollResponse(BaseModel):
    status: str = Field(..., description="pending | confirmed | expired")
    access_token: str | None = None
    refresh_token: str | None = None
    access_expires_in: int | None = None
    refresh_expires_in: int | None = None
    user_id: str | None = None
    email: str | None = None
