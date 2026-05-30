from __future__ import annotations

from pydantic import BaseModel, Field


class ConfirmQrLoginRequest(BaseModel):
    qr_token: str = Field(..., min_length=16, description="Токен из QR-кода")
