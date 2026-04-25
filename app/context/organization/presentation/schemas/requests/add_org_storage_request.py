from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddOrgStorageRequest(BaseModel):
    """
    Тело запроса добавления хранилища организации.

    Атрибуты:
        provider: Провайдер хранилища.
        endpoint: URL эндпоинта.
        bucket: Имя бакета.
        region: Регион.
        access_key: Ключ доступа (открытый текст).
        max_bytes: Максимальный объём.
        max_file_size_bytes: Максимальный размер файла.
        allowed_extensions: Разрешённые расширения.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "S3",
                "endpoint": "https://s3.amazonaws.com",
                "bucket": "my-bucket",
                "region": "us-east-1",
                "access_key": "AKIAIOSFODNN7EXAMPLE",
                "max_bytes": 10737418240,
                "max_file_size_bytes": 104857600,
                "allowed_extensions": [".png", ".jpg", ".pdf"],
            },
        },
    )

    provider: str = Field(
        default="LOCAL",
        max_length=50,
        description="Провайдер хранилища",
        examples=["S3"],
    )
    endpoint: str | None = Field(
        default=None,
        max_length=2048,
        description="URL эндпоинта",
        examples=["https://s3.amazonaws.com"],
    )
    bucket: str = Field(
        default="",
        max_length=255,
        description="Имя бакета",
        examples=["my-bucket"],
    )
    region: str = Field(
        default="",
        max_length=100,
        description="Регион",
        examples=["us-east-1"],
    )
    access_key: str = Field(
        ...,
        description="Ключ доступа (открытый текст)",
    )
    max_bytes: int = Field(
        default=0,
        ge=0,
        description="Максимальный объём (байты)",
        examples=[10737418240],
    )
    max_file_size_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Максимальный размер файла (байты)",
        examples=[104857600],
    )
    allowed_extensions: list[str] | None = Field(
        default=None,
        description="Разрешённые расширения файлов",
        examples=[[".png", ".jpg", ".pdf"]],
    )
