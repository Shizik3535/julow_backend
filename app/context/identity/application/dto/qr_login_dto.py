from __future__ import annotations

from pydantic import BaseModel, Field


class QrLoginCreatedDTO(BaseModel):
    qr_token: str
    expires_at: str
    qr_uri: str
    poll_interval_ms: int = 2000


class QrLoginPollDTO(BaseModel):
    status: str = Field(..., description="pending | confirmed | expired")
    access_token: str | None = None
    refresh_token: str | None = None
    access_expires_in: int | None = None
    refresh_expires_in: int | None = None
    user_id: str | None = None
    email: str | None = None
