from __future__ import annotations

from pydantic import BaseModel, Field


class CreateStorageRequest(BaseModel):
    """Тело запроса на создание хранилища."""

    owner_type: str
    owner_id: str
    provider: str
    max_bytes: int = Field(..., ge=0)
    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None


class UpdateStorageConfigRequest(BaseModel):
    """Тело запроса на обновление конфигурации хранилища."""

    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None


class UpdateStorageQuotaRequest(BaseModel):
    """Тело запроса на обновление квоты."""

    max_bytes: int = Field(..., ge=0)


class SetAllowedFileTypesRequest(BaseModel):
    """Тело запроса на задание разрешённых типов файлов."""

    file_types: list[str] | None = None


class SetMaxFileSizeRequest(BaseModel):
    """Тело запроса на задание макс. размера файла."""

    max_file_size_bytes: int | None = Field(default=None, ge=0)
