from __future__ import annotations

from pydantic import BaseModel, Field


class CreateQrLoginRequest(BaseModel):
    web_origin: str | None = Field(
        default=None,
        description="Origin веб-клиента для HTTPS QR (например https://julow.ru)",
        examples=["https://julow.ru"],
    )
