from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StorageConfigResponse(BaseModel):
    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None
    custom_params: dict[str, str] | None = None


class StorageResponse(BaseModel):
    id: str
    owner_type: str
    owner_id: str
    provider: str
    config: StorageConfigResponse
    max_bytes: int
    used_bytes: int
    used_percent: int = 0
    allowed_file_types: list[str] | None = None
    max_file_size_bytes: int | None = None
    is_encrypted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
