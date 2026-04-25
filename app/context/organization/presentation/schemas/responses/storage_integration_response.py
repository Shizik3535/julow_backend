from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StorageIntegrationResponse(BaseModel):
    """
    Ответ с данными хранилища организации.

    Атрибуты:
        id: UUID хранилища.
        org_id: UUID организации.
        provider: Провайдер хранилища.
        endpoint: URL эндпоинта.
        bucket: Имя бакета.
        region: Регион.
        max_bytes: Максимальный объём.
        used_bytes: Использованный объём.
        max_file_size_bytes: Максимальный размер файла.
        allowed_extensions: Разрешённые расширения.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID хранилища",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        ...,
        description="UUID организации",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    provider: str = Field(
        default="LOCAL",
        description="Провайдер хранилища",
        examples=["S3"],
    )
    endpoint: str | None = Field(
        default=None,
        description="URL эндпоинта",
        examples=["https://s3.amazonaws.com"],
    )
    bucket: str = Field(
        default="",
        description="Имя бакета",
        examples=["my-bucket"],
    )
    region: str = Field(
        default="",
        description="Регион",
        examples=["us-east-1"],
    )
    max_bytes: int = Field(
        default=0,
        description="Максимальный объём (байты)",
        examples=[10737418240],
    )
    used_bytes: int = Field(
        default=0,
        description="Использованный объём (байты)",
        examples=[5368709120],
    )
    max_file_size_bytes: int | None = Field(
        default=None,
        description="Максимальный размер файла (байты)",
        examples=[104857600],
    )
    allowed_extensions: list[str] | None = Field(
        default=None,
        description="Разрешённые расширения файлов",
        examples=[[".png", ".jpg", ".pdf"]],
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
